import asyncio
from multiprocessing import context
from socket import timeout
from urllib.parse import urljoin
from db_manager.db_manager import DatabaseManager
from playwright.async_api import async_playwright
import re
import datetime

class First_Parsing_AptekaRu:
    def __init__(self):
        self.link = "https://apteka.ru/"
        self.db = DatabaseManager()
        self.pharmansyID = 2
        self.semaphore = asyncio.Semaphore(3)
    """
    * Парсинг категорий, создаёт список категорий и их URL
    * Вызывает функцию и вносит данные в базу данных
    """
    async def getCategories(self):
        categories = []
        async with async_playwright() as p:
            # Создаём браузер, контекст для браузера и страницу
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            # Переходим на страницу
            await page.goto(self.link, wait_until="domcontentloaded", timeout = 60000)
            # нажимаем на кнопку чтобы открался каталог с названиями категорий
            await page.locator("button.CatalogPanel__toggle").click()
            # Получаем данные из открывшегося нисподающего мен
            links = page.locator("span.CatalogMenu__category-button a")
            # Получаем количество категорий
            count = await links.count()
            for i in range(count):
                # Получаем ссылку и название категории
                a = links.nth(i)
                # название категории
                name = (await a.inner_text()).strip()
                # составляющая категории ссылка на неё
                href = await a.get_attribute("href")
                categories.append((name, href))

            await context.close()
            await browser.close()

        for category_name, category_url in categories:
            self.db.insert_category(category_name, category_url, self.pharmansyID)

    """
    * Главная функция
    * Получает список категорий из базы данных
    * Запускает асинхронные задачи для парсинга каждой категории
    * Ожидает завершения всех задач и закрывает браузер
    """
    async def getProductsAtCategories(self):
        categories = self.db.get_categories(self.pharmansyID)
        if not categories:
            print("Категории не найдены в базе данных")
            return
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            tasks = [
                self.process_category(context, category_id, category_url)
                for category_id, category_url in categories
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            await context.close()
            await browser.close()

    """

    * Функция для перехода и листания по страницам категории
    * @param context - контекст браузера
    * @param category_id - идентификатор категории
    * @param category_url - URL категории
    """
    async def process_category(self, context, category_id, category_url):
        # функция каоторая получит раздробление на 3 асинхронных
        async with self.semaphore:
            # создаем новую страницу
            page = await context.new_page()
            try:
                # создаём базовый URL для категории
                base_category_url = urljoin(self.link, category_url)
                print(f"\\nПарсим категорию {category_id}: {base_category_url}")
                # получаем последнюю страницу категории
                last_page = await self.get_last_page(page, base_category_url)
                print(f"Найдено страниц: {last_page}")
                # перебираем страницы категории и парсим товары с каждой
                for page_num in range(1, last_page + 1):
                    if page_num == 1:
                        current_url = base_category_url
                    else:
                        separator = "&" if "?" in base_category_url else "?"
                        current_url = f"{base_category_url}{separator}page={page_num}"

                    print(f"\\nОткрываем страницу {page_num}: {current_url}")
                    await self.parse_products_from_page(page, current_url, category_id)

            except Exception as e:
                print(f"Ошибка при парсинге категории {category_id}: {e}")
            finally:
                await page.close()

    """
    * Мини функция для получения последней страницы категории
    * @param page - страница браузера
    * @param base_category_url - URL категории
    * @return last_page - последняя страница категории
    """
    async def get_last_page(self, page, base_category_url):
            await page.goto(base_category_url, wait_until ="domcontentloaded",  timeout=60000)
            # переменная для записи конечной страннциы этой категории
            pagination_links = page.locator("div.Paginator__page a[href*='page=']")
            pagination_count = await pagination_links.count()
            pagination_count = await pagination_links.count()
            last_page = 1
            for i in range(pagination_count):
                link = pagination_links.nth(i)
                text = int(await link.inner_text())

                if text > last_page:
                    last_page = text
            return last_page


    """
    * Мини функция для получения последней страницы категории
    * @param page - страница браузера
    * @param base_category_url - URL категории
    * @return last_page - последняя страница категории
    """
    async def parse_products_from_page(self, page, page_url, category_id):
        try:
            await page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            # подождём, пока карточки реально появятся
            await page.wait_for_selector("div.catalog-card", timeout=15000)

            items = page.locator("div.catalog-card")
            count = await items.count()

            for i in range(count):
                item = items.nth(i)

                # первый <a> внутри карточки
                link = item.locator("a").first
                price = item.locator("span.moneyprice__roubles")
                href = await link.get_attribute("href")

                # читаем текст — у первой ссылки часто нет текста, поэтому лучше взять название по классу
                name_el = item.locator("a.catalog-card__name.emphasis").first
                name = await name_el.inner_text()

                price_text_raw = await price.inner_text()
                price_text = re.sub(r"\D", "", price_text_raw)

                normalized_name = self.normalizator_name(name)
                medicine = self.db.get_medicine_by_trgm_name(normalized_name)
                parse_date = datetime.date.today()
                full_url = urljoin(self.link, href) if href else None

                medicine_id = medicine["id"] if medicine else None

                if price_text and full_url:
                    self.db.insert_price_info(
                        price_text,
                        self.pharmansyID,
                        medicine_id,  # тут может быть None → в БД будет NULL
                        parse_date,
                        full_url
                    )


                # if href:
                #     url = urljoin(self.link, href)
                #     self.db.insert_url_to_medicines(url, category_id)

        except Exception as e:
            print(f"Ошибка при парсинге товаров со траницы {page_url}: {e}")

    def normalizator_name(self, name: str | None) -> str | None:
        if not name:
            return None
        awcleaned = re.sub(r"[^0-9a-zA-Zа-яА-ЯёЁ\s]", "", name)
        cleaned = re.sub(r"\s+", " ", awcleaned).strip()
        return cleaned.lower()

async def main():
    parser = First_Parsing_AptekaRu()
    #await parser.getCategories()
    await parser.getProductsAtCategories()



if __name__ == "__main__":
    asyncio.run(main())
