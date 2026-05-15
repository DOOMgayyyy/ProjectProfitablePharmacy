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
    def __init__(self):
        self.link = "https://old.gosapteka.ru/"
        self.db = DatabaseManager()
        self.pharmansyID= 1
        #
        self.semaphore = asyncio.Semaphore(3)

    def build_full_url(self, url: str) -> str:
        if url.startswith("/"):
            return f"{self.link.rstrip('/')}{url}"
        return url

    async def getCategories(self):
        categories = []
        #задаём сокращённое обращение к функции
        async with async_playwright() as p:
            # указываем, нужный браузер для использования кодом
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            # для работы с ссылкой открываем новую страницу
            page = await context.new_page()
            # получаем данные по ссылке тк код синхрпонный ждём пока странница полностью прогрузится
            await page.goto(self.link, wait_until="domcontentloaded", timeout=60000)
            # обращаемся к более конкретным подкатегориям и получаем a элемент содержащий в себе и ссылку на категорю и русифицированное название
            links = page.locator("div.sub_menu_item a")
            count = await links.count()
            # перебираем все получившиеся ответы по их количеству
            for i in range(count):
                # получаем содержание поля a название
                a = links.nth(i)
                # название категории
                name = (await a.inner_text()).strip()
                # составляющая категории ссылка на неё
                href = await a.get_attribute("href")
                categories.append((name, href))
            #закрываем браузер
            await context.close()
            await browser.close()
        for category_name, category_url in categories:
            self.db.insert_category(category_name, category_url, self.pharmansyID)

    async def getProductsAtCategories(self):
        # получение категорий из баззы данныъ по id аптеки
        categories = self.db.get_categories(self.pharmansyID)
        # проверка на наличие категорий
        if not categories:
            print("Категории не найдены в базе данных")
            return
        # активация парсера
        async with async_playwright() as p:
            # запускаем движок браузера chromium
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            tasks = [
                self.process_category(context, category_id, category_url)
                for category_id, category_url in categories
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            await context.close()
            await browser.close()

    async def get_last_page(self, page, base_category_url):
            await page.goto(base_category_url, wait_until ="domcontentloaded",  timeout=60000)
            # переменная для записи конечной страннциы этой категории
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

    async def process_category(self, context, category_id, category_url):
        # функция каоторая получит раздробление на 3 асинхронных
        async with self.semaphore:
            page = await context.new_page()
            try:
                base_category_url = self.build_full_url(category_url)
                print(f"\\nПарсим категорию {category_id}: {base_category_url}")

                last_page = await self.get_last_page(page, base_category_url)
                print(f"Найдено страниц: {last_page}")

                for page_num in range(1, last_page + 1):
                    if page_num == 1:
                        current_url = base_category_url
                    else:
                        separator = "&" if "?" in base_category_url else "?"
                        current_url = f"{base_category_url}{separator}PAGEN_1={page_num}"

                    print(f"\\nОткрываем страницу {page_num}: {current_url}")
                    await self.parse_products_from_page(page, current_url, category_id)

            except Exception as e:
                print(f"Ошибка при парсинге категории {category_id}: {e}")
            finally:
                await page.close()

    async def parse_products_from_page(self,page, page_url, category_id):
        try:
            # переходим на странницу
            await page.goto(page_url, wait_until = "domcontentloaded", timeout=60000)
            # ищем элементы с конкретным классом
            items = page.locator("div.cat-item")
            # получаем их количество
            # перебираем все полученные элементы
            count = await items.count()
            for i in range(count):
                item = items.nth(i)
                title_link = item.locator("h3 a")
                # получаем ссылку на продукт
                href = await title_link.get_attribute("href")
                # если найденно то заносим в базу данны
                if href:
                    href = self.build_full_url(href)
                    self.db.insert_url_to_medicines(href, category_id)

        except Exception as e:
            print(f"Ошибка при парсинге товаров со траницы {page_url}: {e}")

    async def get_product_at_pages(self):
        #pages = self.db.get_url_at_products()
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

    async def process_product(self, context, id, product_url):
        async with self.semaphore:
            page = await context.new_page()
            try:
                print(f"\\nПарсим страницу {id}: {product_url}")
                await self.inform_from_page(page, product_url, id)

            except Exception as e:
                print(f"Ошибка при парсинге страницы {id}: {e}")
            finally:
                await page.close()

    async def inform_from_page(self, page, product_url, medicine_id):
        try:
            await page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
            # PRICE
            price = await self.search_price(page)

            # MANUFACTURE
            manufacturer = await self.search_manufacturer(page)
            # STANDAT NAME
            name = await self.search_product_name(page)
            # НОМАЛИЗОВАННАЯ ВЕРСИЯ ИМЕНИ
            normalize_name = await self.normalizator_name(name)

            # ссылка на изображение
            image_url = await self.search_image_url(page)

            # DESCRIPTION
            description = await self.search_description(page)

            # Время парсинга страницы
            #
            parse_date = datetime.date.today()


            self.db.update_medicine_info(medicine_id,name,normalize_name,description,manufacturer,image_url)
            if price is not None:
                self.db.insert_price_info(
                    price,
                    self.pharmansyID,
                    medicine_id,
                    parse_date,
                    product_url
                )

            # print(f"\\nID: {medicine_id}")
            # print("URL:", product_url)
            # print("Производитель:", manufacturer)
            # print("Цена (сыро):", price)
            # print("name", name)
            # print("Normalize name", normalize_name)
            # print("Изображение", image_url)
            # print("Описание",description)

        except Exception as e:
            print(f"Ошибка при парсинге {product_url}: {e}")

    async def search_price(self, page):
        try:
            price_locator = page.locator("div.desc-block-product div.price span")
            if await price_locator.count() > 0:
                price = (await price_locator.first.inner_text()).strip()
                price = re.sub(r'\\D', '', price)
                return price
            else:
                return None

        except Exception as e:
            print(f"Не удалось получить цену со страницы {e}")

    async def search_manufacturer(self, page):
        manufacturer_locator = page.locator('div.props div.prop[data-propp="MANUFACTURER"] span.value')
        if await manufacturer_locator.count() > 0:
            manufacturer = (await manufacturer_locator.first.inner_text()).strip()
            return manufacturer
        else:
            return None

    async def search_product_name(self, page):
        name_locator = page.locator("h1")
        if await name_locator.count() > 0:
            name = (await name_locator.first.inner_text()).strip()
            return name
        else:
            return None

    async def normalizator_name(self, name: str | None) -> str | None:
        if not name:
            return None # убираем всё, кроме букв, цифр и пробелов
        awcleaned = re.sub(r"[^0-9a-zA-Zа-яА-ЯёЁ\\\\s]", "", name)
        cleaned = re.sub(r"\\\\s+", " ", awcleaned).strip()
        return cleaned.lower()

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

    async def search_description(self, page):
        description_locator = page.locator(
            'div.tireos_tabs_content_item[data-id="description"] div.application'
        )
        if await description_locator.count() > 0:
            description = await description_locator.first.inner_html()
            return description
        else:
            return None

    async def delete(self):
        self.db.delete_all_medecines()

class First_API_Patsing_GosA:
    def __init__(self):
        self.api_categories_link="https://old.gosapteka.ru/api/catalog/products?"


async def main():
    parser = First_Parsing_GosApteka()
    #await parser.getCategories()
    #await parser.getProductsAtCategories()
    await parser.get_product_at_pages()
    #await parser.delete()

if __name__ == "__main__":
    asyncio.run(main())
# db_manager/db_manager.py
