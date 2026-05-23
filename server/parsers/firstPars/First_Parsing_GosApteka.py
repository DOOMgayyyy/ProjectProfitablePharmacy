import asyncio
from itertools import product
from multiprocessing import context
from socket import timeout
from sre_parse import CATEGORIES
import sys
import re
import datetime
from unicodedata import normalize

from db_manager.db_manager import DatabaseManager
from playwright.async_api import async_playwright


class First_Parsing_GosApteka:
    """
    * Класс для первичного парсинга сайта ГосАптека
    * Отвечает за сбор категорий, ссылок на товары и деталей по каждому товару
    * Использует асинхронный Playwright и базу данных через DatabaseManager
    """
    def __init__(self):
        """
        * Конструктор класса парсера
        * Инициализирует базовый URL аптеки, подключение к БД и семафор
        """
        self.link = "https://old.gosapteka.ru/"
        self.db = DatabaseManager()
        self.pharmansyID = 1
        self.semaphore = asyncio.Semaphore(3)

    """
    * Вспомогательная функция для построения полного URL
    * @param url - относительная или абсолютная ссылка
    * @return полный URL с учётом базового домена аптеки
    """
    def build_full_url(self, url: str) -> str:
        if url.startswith("/"):
            return f"{self.link.rstrip('/')}{url}"
        return url

    """
    * Функция для получения списка категорий с главной страницы аптеки
    * Открывает сайт, собирает названия и ссылки категорий и сохраняет их в БД
    """
    async def getCategories(self):
        categories = []
        async with async_playwright() as p:
            # указываем нужный браузер для использования кодом
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            # открываем новую страницу
            page = await context.new_page()
            # переходим на главную страницу и ждём загрузки DOM
            await page.goto(self.link, wait_until="domcontentloaded", timeout=60000)
            # получаем список ссылок на подкатегории
            links = page.locator("div.sub_menu_item a")
            count = await links.count()
            # перебираем все найденные категории
            for i in range(count):
                a = links.nth(i)
                name = (await a.inner_text()).strip()
                href = await a.get_attribute("href")
                categories.append((name, href))
            # закрываем браузер
            await context.close()
            await browser.close()

        # сохраняем категории в БД
        for category_name, category_url in categories:
            self.db.insert_category(category_name, category_url, self.pharmansyID)

    """
    * Главная функция парсинга категорий
    * Получает список категорий из БД и запускает асинхронный парсинг каждой категории
    """
    async def getProductsAtCategories(self):
        # получение категорий из базы данных по id аптеки
        categories = self.db.get_categories(self.pharmansyID)
        if not categories:
            print("Категории не найдены в базе данных")
            return

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            # запускаем обработку категорий параллельно с ограничением семафора
            tasks = [
                self.process_category(context, category_id, category_url)
                for category_id, category_url in categories
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            await context.close()
            await browser.close()

    """
    * Мини-функция для получения последней страницы категории
    * @param page - страница браузера
    * @param base_category_url - URL категории
    * @return last_page - номер последней страницы категории
    """
    async def get_last_page(self, page, base_category_url):
        await page.goto(base_category_url, wait_until="domcontentloaded", timeout=60000)
        last_page = 1

        pagination_links = page.locator(
            "div.bx_pagination_page ul a[href*='PAGEN_1=']"
        )
        pagination_count = await pagination_links.count()

        for i in range(pagination_count):
            href = await pagination_links.nth(i).get_attribute("href")
            if href and "PAGEN_1=" in href:
                try:
                    page_num = int(href.split("PAGEN_1=")[1].split("&")[0])
                    if page_num > last_page:
                        last_page = page_num
                except ValueError:
                    pass

        return last_page

    """
    * Функция для обработки одной категории
    * Открывает страницу категории, определяет количество страниц и парсит каждую страницу
    * @param context - контекст браузера
    * @param category_id - id категории в БД
    * @param category_url - относительный или полный URL категории
    """
    async def process_category(self, context, category_id, category_url):
        async with self.semaphore:
            page = await context.new_page()
            try:
                base_category_url = self.build_full_url(category_url)
                print(f"\nПарсим категорию {category_id}: {base_category_url}")

                last_page = await self.get_last_page(page, base_category_url)
                print(f"Найдено страниц: {last_page}")

                for page_num in range(1, last_page + 1):
                    if page_num == 1:
                        current_url = base_category_url
                    else:
                        separator = "&" if "?" in base_category_url else "?"
                        current_url = f"{base_category_url}{separator}PAGEN_1={page_num}"

                    print(f"\nОткрываем страницу {page_num}: {current_url}")
                    await self.parse_products_from_page(page, current_url, category_id)

            except Exception as e:
                print(f"Ошибка при парсинге категории {category_id}: {e}")
            finally:
                await page.close()

    """
    * Функция для получения ссылок на товары со страницы категории
    * @param page - страница браузера
    * @param page_url - URL конкретной страницы категории
    * @param category_id - id категории в БД
    """
    async def parse_products_from_page(self, page, page_url, category_id):
        try:
            await page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            items = page.locator("div.cat-item")
            count = await items.count()
            for i in range(count):
                item = items.nth(i)
                title_link = item.locator("h3 a")
                href = await title_link.get_attribute("href")
                if href:
                    href = self.build_full_url(href)
                    self.db.insert_url_to_medicines(href, category_id)

        except Exception as e:
            print(f"Ошибка при парсинге товаров со страницы {page_url}: {e}")

    """
    * Функция для запуска парсинга по всем сохранённым товарам
    * Получает список URL товаров из БД и запускает обработку каждой страницы товара
    """
    async def get_product_at_pages(self):
        pages = self.db.get_url_at_products()
        if not pages:
            print("Товары не были найдены")
            return

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            tasks = [
                self.process_product(context, id, product_url)
                for id, product_url in pages
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            await context.close()
            await browser.close()

    """
    * Функция для обработки одной страницы товара
    * @param context - контекст браузера
    * @param id - id товара в БД
    * @param product_url - URL страницы товара
    """
    async def process_product(self, context, id, product_url):
        async with self.semaphore:
            page = await context.new_page()
            try:
                print(f"\nПарсим страницу {id}: {product_url}")
                await self.inform_from_page(page, product_url, id)
            except Exception as e:
                print(f"Ошибка при парсинге страницы {id}: {e}")
            finally:
                await page.close()

    """
    * Функция для получения подробной информации с страницы товара
    * Собирает цену, производителя, название, нормализованное название,
    * описание и ссылку на изображение, и сохраняет их в БД
    * @param page - страница браузера
    * @param product_url - URL страницы товара
    * @param medicine_id - id товара в таблице medicines
    """
    async def inform_from_page(self, page, product_url, medicine_id):
        try:
            await page.goto(product_url, wait_until="domcontentloaded", timeout=60000)

            price = await self.search_price(page)
            manufacturer = await self.search_manufacturer(page)
            name = await self.search_product_name(page)
            normalize_name = await self.normalizator_name(name)
            image_url = await self.search_image_url(page)
            description = await self.search_description(page)
            parse_date = datetime.date.today()

            self.db.update_medicine_info(
                medicine_id, name, normalize_name, description, manufacturer, image_url
            )

            if price is not None:
                self.db.insert_price_info(
                    price,
                    self.pharmansyID,
                    medicine_id,
                    parse_date,
                    product_url
                )

        except Exception as e:
            print(f"Ошибка при парсинге {product_url}: {e}")

    """
    * Функция для поиска и очистки цены товара на странице
    * @param page - страница браузера
    * @return цена в виде строки только с цифрами или None, если не найдено
    """
    async def search_price(self, page):
        try:
            price_locator = page.locator("div.desc-block-product div.price span")
            if await price_locator.count() > 0:
                price = (await price_locator.first.inner_text()).strip()
                price = re.sub(r'\D', '', price)
                return price
            else:
                return None

        except Exception as e:
            print(f"Не удалось получить цену со страницы {e}")

    """
    * Функция для поиска производителя товара на странице
    * @param page - страница браузера
    * @return строка с названием производителя или None, если не найдено
    """
    async def search_manufacturer(self, page):
        manufacturer_locator = page.locator(
            'div.props div.prop[data-propp="MANUFACTURER"] span.value'
        )
        if await manufacturer_locator.count() > 0:
            manufacturer = (await manufacturer_locator.first.inner_text()).strip()
            return manufacturer
        else:
            return None

    """
    * Функция для поиска стандартного названия товара на странице
    * @param page - страница браузера
    * @return строка с названием товара или None, если не найдено
    """
    async def search_product_name(self, page):
        name_locator = page.locator("h1")
        if await name_locator.count() > 0:
            name = (await name_locator.first.inner_text()).strip()
            return name
        else:
            return None

    """
    * Функция для нормализации названия товара
    * Убирает все символы, кроме букв, цифр и пробелов, схлопывает пробелы и приводит к нижнему регистру
    * @param name - исходное название товара или None
    * @return нормализованная строка или None, если name пустое
    """
    async def normalizator_name(self, name: str | None) -> str | None:
        if not name:
            return None
        awcleaned = re.sub(r"[^0-9a-zA-Zа-яА-ЯёЁ\\\\s]", "", name)
        cleaned = re.sub(r"\\\\s+", " ", awcleaned).strip()
        return cleaned.lower()

    """
    * Функция для получения ссылки на изображение товара
    * @param page - страница браузера
    * @return полный URL изображения или None, если не найдено
    """
    async def search_image_url(self, page):
        image_locator = page.locator("div.main-img-product img")
        if await image_locator.count() > 0:
            src = await image_locator.first.get_attribute("src")
        else:
            src = None
        if src:
            image_url = self.build_full_url(src)
            return image_url
        else:
            return None

    """
    * Функция для получения HTML-описания товара
    * @param page - страница браузера
    * @return HTML-строка с описанием или None, если не найдено
    """
    async def search_description(self, page):
        description_locator = page.locator(
            'div.tireos_tabs_content_item[data-id="description"] div.application'
        )
        if await description_locator.count() > 0:
            description = await description_locator.first.inner_html()
            return description
        else:
            return None


"""
* Точка входа для запуска парсера ГосАптеки
* Можно по очереди запускать сбор категорий, товаров и деталей по товарам
"""
async def main():
    parser = First_Parsing_GosApteka()
    # await parser.getCategories()
    # await parser.getProductsAtCategories()
    await parser.get_product_at_pages()
    # await parser.delete()


if __name__ == "__main__":
    asyncio.run(main())
