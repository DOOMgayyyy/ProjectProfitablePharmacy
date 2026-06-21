import asyncio
import re
import datetime
import sys

from db_manager.db_manager import DatabaseManager
from playwright.async_api import async_playwright


class ReParse_Gosapteka:
    """
    * Класс для повторного парсинга цен с сайта ГосАптека
    * Берёт уже известные URL из таблицы prices, заново заходит на каждую страницу
    * и обновляет цену в существующей записи через update_price
    """

    def __init__(self):
        """
        * Конструктор класса
        * Инициализирует базовый URL аптеки, подключение к БД и семафор
        """
        self.link = "https://old.gosapteka.ru/"
        self.db = DatabaseManager()
        self.pharmansyID = 1
        self.semaphore = asyncio.Semaphore(3)

    """
    * Вспомогательная функция для построения полного URL
    * @param url - относительная или абсолютная ссылка
    * @return полный URL
    """
    def build_full_url(self, url: str) -> str:
        if url.startswith("/"):
            return f"{self.link.rstrip('/')}{url}"
        return url

    """
    * Главная функция запуска репарсинга
    * Получает список URL из prices, запускает асинхронный обход каждой страницы
    """
    async def run(self):
        rows = self.db.get_urls_from_prices(self.pharmansyID)
        if not rows:
            print("Нет URL для репарсинга ГосАптека")
            return

        print(f"Найдено {len(rows)} URL для обновления цен (ГосАптека)")

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
                await page.goto(medicine_url, wait_until="domcontentloaded", timeout=60000)

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
    * Функция для поиска и очистки цены товара на странице ГосАптеки
    * @param page - страница браузера
    * @return цена в виде строки только с цифрами или None, если не найдено
    """
    async def search_price(self, page):
        try:
            price_locator = page.locator("div.desc-block-product div.price span")
            if await price_locator.count() > 0:
                price = (await price_locator.first.inner_text()).strip()
                price = re.sub(r'\D', '', price)
                return price if price else None
            return None
        except Exception as e:
            print(f"  Не удалось получить цену: {e}")
            return None


"""
* Точка входа для запуска репарсера ГосАптеки
"""
async def main():
    parser = ReParse_Gosapteka()
    await parser.run()


if __name__ == "__main__":
    asyncio.run(main())
