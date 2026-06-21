import asyncio
import re
import datetime
from urllib.parse import urljoin

from db_manager.db_manager import DatabaseManager
from playwright.async_api import async_playwright


class ReParse_AptekaRu:
    """
    * Класс для повторного парсинга цен с сайта Apteka.ru
    * Берёт уже известные URL из таблицы prices, заново заходит на каждую страницу
    * и обновляет цену в существующей записи через update_price
    """

    def __init__(self):
        """
        * Конструктор класса
        * Инициализирует базовый URL аптеки, подключение к БД и семафор
        """
        self.link = "https://apteka.ru/"
        self.db = DatabaseManager()
        self.pharmansyID = 2
        self.semaphore = asyncio.Semaphore(3)

    """
    * Главная функция запуска репарсинга
    * Получает список URL из prices, запускает асинхронный обход каждой страницы
    """
    async def run(self):
        rows = self.db.get_urls_from_prices(self.pharmansyID)
        if not rows:
            print("Нет URL для репарсинга Apteka.ru")
            return

        print(f"Найдено {len(rows)} URL для обновления цен (Apteka.ru)")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            tasks = [
                self.process_url(context, price_id, medicine_id, medicine_url)
                for price_id, medicine_id, medicine_url in rows
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

            await context.close()
            await browser.close()

    """
    * Функция обработки одной записи из prices
    * Открывает страницу товара, ищет цену и обновляет запись в БД
    * @param context - контекст браузера
    * @param price_id - id записи в таблице prices
    * @param medicine_id - id лекарства (для логирования)
    * @param medicine_url - URL страницы товара
    """
    async def process_url(self, context, price_id, medicine_id, medicine_url):
        async with self.semaphore:
            page = await context.new_page()
            try:
                print(f"Репарсим (id={price_id}): {medicine_url}")
                full_url = urljoin(self.link, medicine_url)
                await page.goto(full_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_selector("span.moneyprice__roubles", timeout=15000)

                new_price = await self.search_price(page)
                if new_price is None:
                    print(f"  Цена не найдена: {medicine_url}")
                    return

                parse_date = datetime.date.today()
                self.db.update_price(price_id, new_price, parse_date)
                print(f"  Обновлено: price_id={price_id}, новая цена={new_price}")

            except Exception as e:
                print(f"  Ошибка при репарсинге {medicine_url}: {e}")
            finally:
                await page.close()

    """
    * Функция для поиска и очистки цены товара на странице Apteka.ru
    * @param page - страница браузера
    * @return цена в виде строки только с цифрами или None, если не найдено
    """
    async def search_price(self, page):
        try:
            price_locator = page.locator("span.moneyprice__roubles")
            if await price_locator.count() > 0:
                price_text = (await price_locator.first.inner_text()).strip()
                price = re.sub(r'\D', '', price_text)
                return price if price else None
            return None
        except Exception as e:
            print(f"  Не удалось получить цену: {e}")
            return None


"""
* Точка входа для запуска репарсера Apteka.ru
"""
async def main():
    parser = ReParse_AptekaRu()
    await parser.run()


if __name__ == "__main__":
    asyncio.run(main())
