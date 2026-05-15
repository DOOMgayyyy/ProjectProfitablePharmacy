import asyncio
from itertools import product
from multiprocessing import context
from socket import timeout
from sre_parse import CATEGORIES
import sys
import re
from unicodedata import normalize

from db_manager.db_manager import DatabaseManager
from playwright.async_api import async_playwright

class First_Parsing_GosApteka:
    def __init__(self):
        self.link = "https://gosapteka.ru/"
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

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(self.link, wait_until="domcontentloaded", timeout=60000)
            links = page.locator("div.sub_menu_item a")
            count = await links.count()
            for i in range(count):
                a = links.nth(i)
                name = (await a.inner_text()).strip()
                href = await a.get_attribute("href")
                categories.append((name, href))
            await context.close()
            await browser.close()
        for category_name, category_url in categories:
            self.db.insert_category(category_name, category_url, self.pharmansyID)

    async def getProductsAtCategories(self):
        # получение категорий из базы данных
        categories = self.db.get_categories(self.pharmansyID)
        if not categories:
            print("Не удалось получить категории из базы данных")
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


    async def process_category(self, context, category_id, category_url):
        async with self.semaphore:
            page = await context.new_page()
            try:
                base_category_url = self.build_full_url(category_url)
                print(f"\nÐŸÐ°Ñ€ÑÐ¸Ð¼ ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸ÑŽ {category_id}: {base_category_url}")

                last_page = await self.get_last_page(page, base_category_url)
                print(f"ÐÐ°Ð¹Ð´ÐµÐ½Ð¾ ÑÑ‚Ñ€Ð°Ð½Ð¸Ñ†: {last_page}")

                for page_num in range(1, last_page + 1):
                    if page_num == 1:
                        current_url = base_category_url
                    else:
                        separator = "&" if "?" in base_category_url else "?"
                        current_url = f"{base_category_url}{separator}PAGEN_1={page_num}"

                    print(f"\nÐžÑ‚ÐºÑ€Ñ‹Ð²Ð°ÐµÐ¼ ÑÑ‚Ñ€Ð°Ð½Ð¸Ñ†Ñƒ {page_num}: {current_url}")
                    await self.parse_products_from_page(page, current_url, category_id)

            except Exception as e:
                print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð¿Ñ€Ð¸ Ð¿Ð°Ñ€ÑÐ¸Ð½Ð³Ðµ ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ð¸ {category_id}: {e}")
            finally:
                await page.close()

    async def get_last_page(self, page, base_category_url):
            await page.goto(base_category_url, wait_until ="domcontentloaded",  timeout=60000)
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

    async def parse_products_from_page(self,page, page_url, category_id):
        try:
            await page.goto(page_url, wait_until = "domcontentloaded", timeout=60000)
            items = page.locator("div.cat-item")
            count = await items.count()
            for i in range(count):
                item = items.nth(i)
                title_link = item.locator("h3 a")
                # Ð¿Ð¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ ÑÑÑ‹Ð»ÐºÑƒ Ð½Ð° Ð¿Ñ€Ð¾Ð´ÑƒÐºÑ‚
                href = await title_link.get_attribute("href")
                if href:
                    href = self.build_full_url(href)
                    self.db.insert_url_to_medicines(href, category_id)

        except Exception as e:
            print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð¿Ñ€Ð¸ Ð¿Ð°Ñ€ÑÐ¸Ð½Ð³Ðµ Ñ‚Ð¾Ð²Ð°Ñ€Ð¾Ð² ÑÐ¾ Ñ‚Ñ€Ð°Ð½Ð¸Ñ†Ñ‹ {page_url}: {e}")

    async def get_product_at_pages(self):
        #pages = self.db.get_url_at_products()
        pages = [ (695, 'https://gosapteka.ru/catalog/voda_i_napitki/14076801_kisel_leovit_zheludochnyy_neytralnyy_20g_5_pak_art_14076801/'), (700, 'https://gosapteka.ru/catalog/dieticheskoe_pitanie/21677801_911_vasha_sluzhba_spaseniya_ledentsy_koren_solodki_chabrets_s_vitam_s_b_sakh_2_5g_50g_art_21677801/')]
        if not pages:
            print("Ð¢Ð¾Ð²Ð°Ñ€Ñ‹ Ð½Ðµ Ð±Ñ‹Ð»Ð¸ Ð½Ð°Ð¹Ð´ÐµÐ½Ñ‹")
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
                print(f"\nÐŸÐ°Ñ€ÑÐ¸Ð¼ ÑÑ‚Ñ€Ð°Ð½Ð¸Ñ†Ñƒ {id}: {product_url}")
                await self.inform_from_page(page, product_url, id)

            except Exception as e:
                print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð¿Ñ€Ð¸ Ð¿Ð°Ñ€ÑÐ¸Ð½Ð³Ðµ ÑÑ‚Ñ€Ð°Ð½Ð¸Ñ†Ñ‹ {id}: {e}")
            finally:
                await page.close()

    async def inform_from_page(self, page, product_url, medicine_id):
        try:
            await page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
            # PRICE
            price = self.search_price(page)

            # MANUFACTURE
            manufacturer = self.search_manufacturer(page)
            # STANDAT NAME
            name = self.search_product_name(page)
            # ÐÐžÐœÐÐ›Ð˜Ð—ÐžÐ’ÐÐÐÐÐ¯ Ð’Ð•Ð Ð¡Ð˜Ð¯ Ð˜ÐœÐ•ÐÐ˜
            normalize_name = self.normalizator_name(name)

            # ÑÑÑ‹Ð»ÐºÐ° Ð½Ð° Ð¸Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ðµ
            image_url = self.search_image_url(page)

            # DESCRIPTION
            description = self.search_description(page)





            print(f"\nID: {medicine_id}")
            print("URL:", product_url)
            print("ÐŸÑ€Ð¾Ð¸Ð·Ð²Ð¾Ð´Ð¸Ñ‚ÐµÐ»ÑŒ:", manufacturer)
            print("Ð¦ÐµÐ½Ð° (ÑÑ‹Ñ€Ð¾):", price)
            print("name", name)
            print("Normalize name", normalize_name)
            print("Ð˜Ð·Ð¾Ð±Ñ€Ð°Ð¶ÐµÐ½Ð¸Ðµ", image_url)
            print("ID ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ð¸")
            print("ÐžÐ¿Ð¸ÑÐ°Ð½Ð¸Ðµ",description)

        except Exception as e:
            print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð¿Ñ€Ð¸ Ð¿Ð°Ñ€ÑÐ¸Ð½Ð³Ðµ {product_url}: {e}")

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
            print(f"ÐÐµ ÑƒÐ´Ð°Ð»Ð¾ÑÑŒ Ð¿Ð¾Ð»ÑƒÑ‡Ð¸Ñ‚ÑŒ Ñ†ÐµÐ½Ñƒ ÑÐ¾ ÑÑ‚Ñ€Ð°Ð½Ð¸Ñ†Ñ‹ {e}")

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
            return None
        # ÑƒÐ±Ð¸Ñ€Ð°ÐµÐ¼ Ð²ÑÑ‘, ÐºÑ€Ð¾Ð¼Ðµ Ð±ÑƒÐºÐ², Ñ†Ð¸Ñ„Ñ€ Ð¸ Ð¿Ñ€Ð¾Ð±ÐµÐ»Ð¾Ð²
        awcleaned = re.sub(r"[^0-9a-zA-ZÐ°-ÑÐ-Ð¯Ñ‘Ð\s]", " ", name)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
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


async def main():
    parser = First_Parsing_GosApteka()
    #await parser.getCategories()
    #await parser.getProductsAtCategories()
    await parser.get_product_at_pages()

if __name__ == "__main__":
    asyncio.run(main())
