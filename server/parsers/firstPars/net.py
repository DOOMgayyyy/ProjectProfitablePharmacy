from db_manager.db_manager import DatabaseManager
from playwright.async_api import async_playwright
import asyncio

class net:
    def __init__(self):
        self.link = "https://178.248.235.161/"
        self.db = DatabaseManager()
        self.pharmansyID= 1
        #
        self.semaphore = asyncio.Semaphore(3)

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
            html = await page.content()
            print(html)


async def main():
    parser = net()
    await parser.getCategories()
    #await parser.getProductsAtCategories()
    #await parser.delete()

if __name__ == "__main__":
    asyncio.run(main())
