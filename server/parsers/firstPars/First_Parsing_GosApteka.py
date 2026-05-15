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
        #Ð·Ð°Ð´Ð°Ñ‘Ð¼ ÑÐ¾ÐºÑ€Ð°Ñ‰Ñ‘Ð½Ð½Ð¾Ðµ Ð¾Ð±Ñ€Ð°Ñ‰ÐµÐ½Ð¸Ðµ Ðº Ñ„ÑƒÐ½ÐºÑ†Ð¸Ð¸
        async with async_playwright() as p:
            # ÑƒÐºÐ°Ð·Ñ‹Ð²Ð°ÐµÐ¼, Ð½ÑƒÐ¶Ð½Ñ‹Ð¹ Ð±Ñ€Ð°ÑƒÐ·ÐµÑ€ Ð´Ð»Ñ Ð¸ÑÐ¿Ð¾Ð»ÑŒÐ·Ð¾Ð²Ð°Ð½Ð¸Ñ ÐºÐ¾Ð´Ð¾Ð¼
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            # Ð´Ð»Ñ Ñ€Ð°Ð±Ð¾Ñ‚Ñ‹ Ñ ÑÑÑ‹Ð»ÐºÐ¾Ð¹ Ð¾Ñ‚ÐºÑ€Ñ‹Ð²Ð°ÐµÐ¼ Ð½Ð¾Ð²ÑƒÑŽ ÑÑ‚Ñ€Ð°Ð½Ð¸Ñ†Ñƒ
            page = await context.new_page()
            # Ð¿Ð¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ð´Ð°Ð½Ð½Ñ‹Ðµ Ð¿Ð¾ ÑÑÑ‹Ð»ÐºÐµ Ñ‚Ðº ÐºÐ¾Ð´ ÑÐ¸Ð½Ñ…Ñ€Ð¿Ð¾Ð½Ð½Ñ‹Ð¹ Ð¶Ð´Ñ‘Ð¼ Ð¿Ð¾ÐºÐ° ÑÑ‚Ñ€Ð°Ð½Ð½Ð¸Ñ†Ð° Ð¿Ð¾Ð»Ð½Ð¾ÑÑ‚ÑŒÑŽ Ð¿Ñ€Ð¾Ð³Ñ€ÑƒÐ·Ð¸Ñ‚ÑÑ
            await page.goto(self.link, wait_until="domcontentloaded", timeout=60000)
            # Ð¾Ð±Ñ€Ð°Ñ‰Ð°ÐµÐ¼ÑÑ Ðº Ð±Ð¾Ð»ÐµÐµ ÐºÐ¾Ð½ÐºÑ€ÐµÑ‚Ð½Ñ‹Ð¼ Ð¿Ð¾Ð´ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸ÑÐ¼ Ð¸ Ð¿Ð¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ a ÑÐ»ÐµÐ¼ÐµÐ½Ñ‚ ÑÐ¾Ð´ÐµÑ€Ð¶Ð°Ñ‰Ð¸Ð¹ Ð² ÑÐµÐ±Ðµ Ð¸ ÑÑÑ‹Ð»ÐºÑƒ Ð½Ð° ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€ÑŽ Ð¸ Ñ€ÑƒÑÐ¸Ñ„Ð¸Ñ†Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð½Ð¾Ðµ Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ
            links = page.locator("div.sub_menu_item a")
            count = await links.count()
            # Ð¿ÐµÑ€ÐµÐ±Ð¸Ñ€Ð°ÐµÐ¼ Ð²ÑÐµ Ð¿Ð¾Ð»ÑƒÑ‡Ð¸Ð²ÑˆÐ¸ÐµÑÑ Ð¾Ñ‚Ð²ÐµÑ‚Ñ‹ Ð¿Ð¾ Ð¸Ñ… ÐºÐ¾Ð»Ð¸Ñ‡ÐµÑÑ‚Ð²Ñƒ
            for i in range(count):
                # Ð¿Ð¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ ÑÐ¾Ð´ÐµÑ€Ð¶Ð°Ð½Ð¸Ðµ Ð¿Ð¾Ð»Ñ a Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ
                a = links.nth(i)
                # Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ð¸
                name = (await a.inner_text()).strip()
                # ÑÐ¾ÑÑ‚Ð°Ð²Ð»ÑÑŽÑ‰Ð°Ñ ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ð¸ ÑÑÑ‹Ð»ÐºÐ° Ð½Ð° Ð½ÐµÑ‘
                href = await a.get_attribute("href")
                categories.append((name, href))
            #Ð·Ð°ÐºÑ€Ñ‹Ð²Ð°ÐµÐ¼ Ð±Ñ€Ð°ÑƒÐ·ÐµÑ€
            await context.close()
            await browser.close()
        for category_name, category_url in categories:
            self.db.insert_category(category_name, category_url, self.pharmansyID)

    async def getProductsAtCategories(self):
        # Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð¸Ðµ ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ð¹ Ð¸Ð· Ð±Ð°Ð·Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹ÑŠ Ð¿Ð¾ id Ð°Ð¿Ñ‚ÐµÐºÐ¸
        categories = self.db.get_categories(self.pharmansyID)
        # Ð¿Ñ€Ð¾Ð²ÐµÑ€ÐºÐ° Ð½Ð° Ð½Ð°Ð»Ð¸Ñ‡Ð¸Ðµ ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ð¹
        if not categories:
            print("ÐšÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ð¸ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½Ñ‹ Ð² Ð±Ð°Ð·Ðµ Ð´Ð°Ð½Ð½Ñ‹Ñ…")
            return
        # Ð°ÐºÑ‚Ð¸Ð²Ð°Ñ†Ð¸Ñ Ð¿Ð°Ñ€ÑÐµÑ€Ð°
        async with async_playwright() as p:
            # Ð·Ð°Ð¿ÑƒÑÐºÐ°ÐµÐ¼ Ð´Ð²Ð¸Ð¶Ð¾Ðº Ð±Ñ€Ð°ÑƒÐ·ÐµÑ€Ð° chromium
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
            # Ð¿ÐµÑ€ÐµÐ¼ÐµÐ½Ð½Ð°Ñ Ð´Ð»Ñ Ð·Ð°Ð¿Ð¸ÑÐ¸ ÐºÐ¾Ð½ÐµÑ‡Ð½Ð¾Ð¹ ÑÑ‚Ñ€Ð°Ð½Ð½Ñ†Ð¸Ñ‹ ÑÑ‚Ð¾Ð¹ ÐºÐ°Ñ‚ÐµÐ³Ð¾Ñ€Ð¸Ð¸
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
        # Ñ„ÑƒÐ½ÐºÑ†Ð¸Ñ ÐºÐ°Ð¾Ñ‚Ð¾Ñ€Ð°Ñ Ð¿Ð¾Ð»ÑƒÑ‡Ð¸Ñ‚ Ñ€Ð°Ð·Ð´Ñ€Ð¾Ð±Ð»ÐµÐ½Ð¸Ðµ Ð½Ð° 3 Ð°ÑÐ¸Ð½Ñ…Ñ€Ð¾Ð½Ð½Ñ‹Ñ…
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

    async def parse_products_from_page(self,page, page_url, category_id):
        try:
            # Ð¿ÐµÑ€ÐµÑ…Ð¾Ð´Ð¸Ð¼ Ð½Ð° ÑÑ‚Ñ€Ð°Ð½Ð½Ð¸Ñ†Ñƒ
            await page.goto(page_url, wait_until = "domcontentloaded", timeout=60000)
            # Ð¸Ñ‰ÐµÐ¼ ÑÐ»ÐµÐ¼ÐµÐ½Ñ‚Ñ‹ Ñ ÐºÐ¾Ð½ÐºÑ€ÐµÑ‚Ð½Ñ‹Ð¼ ÐºÐ»Ð°ÑÑÐ¾Ð¼
            items = page.locator("div.cat-item")
            # Ð¿Ð¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ Ð¸Ñ… ÐºÐ¾Ð»Ð¸Ñ‡ÐµÑÑ‚Ð²Ð¾
            # Ð¿ÐµÑ€ÐµÐ±Ð¸Ñ€Ð°ÐµÐ¼ Ð²ÑÐµ Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð½Ñ‹Ðµ ÑÐ»ÐµÐ¼ÐµÐ½Ñ‚Ñ‹
            count = await items.count()
            for i in range(count):
                item = items.nth(i)
                title_link = item.locator("h3 a")
                # Ð¿Ð¾Ð»ÑƒÑ‡Ð°ÐµÐ¼ ÑÑÑ‹Ð»ÐºÑƒ Ð½Ð° Ð¿Ñ€Ð¾Ð´ÑƒÐºÑ‚
                href = await title_link.get_attribute("href")
                # ÐµÑÐ»Ð¸ Ð½Ð°Ð¹Ð´ÐµÐ½Ð½Ð¾ Ñ‚Ð¾ Ð·Ð°Ð½Ð¾ÑÐ¸Ð¼ Ð² Ð±Ð°Ð·Ñƒ Ð´Ð°Ð½Ð½Ñ‹
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
