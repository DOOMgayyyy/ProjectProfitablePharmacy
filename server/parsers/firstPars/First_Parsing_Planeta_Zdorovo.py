import asyncio
from unicodedata import category

from playwright.async_api import async_playwright

from db_manager.db_manager import DatabaseManager


class First_Parsing_Planeta_Zdorovo:
    def __init__(self):
        self.link = "https://planetazdorovo.ru/"
        self.db = DatabaseManager()
        self.pharmansyID = 2

        self.semaphore = asyncio.Semaphore(3)

    async def _getCategoties(self):
        categories = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(self.link, wait_until="domcontentloaded", timeout=60000)
            links = page.locator("li.popup-catalog__item a")
            count = await links.count()
            for i in range(count):
                # получаем содержание поля a название
                a = links.nth(i)
                # название категории
                name = (await a.inner_text()).strip()
                # составляющая категории ссылка на неё
                href = await a.get_attribute("href")
                print(name, href)



async def main():
    parser = First_Parsing_Planeta_Zdorovo()
    #await parser.getCategories()
    #await parser.getProductsAtCategories()
    await parser._getCategoties()
    #await parser.delete()

if __name__ == "__main__":
    asyncio.run(main())
# db_manager/db_manager.py
