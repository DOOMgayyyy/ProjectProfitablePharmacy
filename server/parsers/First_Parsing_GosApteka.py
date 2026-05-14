import os
import psycopg
import asyncio
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

class First_Parsing_GosApteka:
  def __init__(self):
    #указываем ссылку ан нашу целевую страницу
    self.link  = "https://gosapteka.ru/"
    self.dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(self.dotenv_path)

    self.conninfo = (
        f"host={os.getenv('DB_URL')} "
        f"port={os.getenv('DB_PORT')} "
        f"dbname={os.getenv('DB_NAME')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASS')}"
    )


  async def getCategories(self):
    categories = []

    #задаём сокращённое обращение к функции
    with sync_playwright() as p:
      # указываем, нужный браузер для использования кодом
      browser = p.chromium.launch(headless=False)
      # для работы с ссылкой открываем новую страницу
      page = browser.new_page()
      # получаем данные по ссылке тк код синхрпонный ждём пока странница полностью прогрузится
      page.goto(self.link)
      # получаем содержимое внутри интересующего нас div
      #menu = page.locator("div.catalog_sub_menu")
      # обращаемся к более конкретным подкатегориям и получаем a элемент содержащий в себе и ссылку на категорю и русифицированное название
      links = page.locator("div.sub_menu_item a")
      # перебираем все получившиеся ответы по их количеству
      for i in range(links.count()):
        # получаем содержание поля a название
        a = links.nth(i)

        # название категории
        name = a.inner_text().strip()

        # составляющая категории ссылка на неё
        href = a.get_attribute("href")

        categories.append((name, href))
      browser.close()
    for category_name, category_url in categories:
      await self.setToDataBase(category_name, category_url)

  #асинхронный вызов функции с параметрами конструктора, передаём название категории и
  async def setToDataBase(self, category_name, categories_url, pharmacy_id=1):
    try:
      # асинхронный вызов асинхронного подключения к базе данных
      async with await psycopg.AsyncConnection.connect(self.conninfo) as conn:
        # асинхронный вызов инструмента для взаимодейставия с базой данных
        async with conn.cursor() as cur:
            # не асинхронная функция добавленияв базу данных
              await cur.execute(
                  "INSERT INTO categories (category_name, categories_url, pharmacy_id)VALUES (%s, %s, %s)",
                  (category_name, categories_url, pharmacy_id)
              )

    except psycopg.Error as e:
      print(f"Ошибка базы данных: {e}")

  # получаем категории из базы данных
  async def getCategoriesFromDB(self):
    try:
      # асинхронный вызов асинхронного подключения к базе данных
      async with await psycopg.AsyncConnection.connect(self.conninfo) as conn:
        # асинхронный вызов инструмента для взаимодейставия с базой данных
        async with conn.cursor() as cur:
          await cur.execute(
            "SELECT category_name, categories_url FROM categories"
          )
          categories = await cur.fetchall()
          return categories
    except psycopg.Error as e:
      print(f"Ошибка базы данных: {e}")
      return []

  # сохраняем товары в базу данных
  async def setProductToDataBase(self, product_name, product_url, category_name):
    try:
      # асинхронный вызов асинхронного подключения к базе данных
      async with await psycopg.AsyncConnection.connect(self.conninfo) as conn:
        # асинхронный вызов инструмента для взаимодейставия с базой данных
        async with conn.cursor() as cur:
          await cur.execute(
            "INSERT INTO products (product_name, product_url, category_name) VALUES (%s, %s, %s)",
            (product_name, product_url, category_name)
          )
    except psycopg.Error as e:
      print(f"Ошибка базы данных: {e}")


  async def getProductsAtCategories(self):
      # получаем категории из базы данных
      categories = await self.getCategoriesFromDB()
      print (categories)

      if not categories:
        print("Категории не найдены в базе данных")
        return

      # перебираем категории из бд
      for category_name, category_url in categories:
        try:
          with sync_playwright() as p:
            # переход на страницу категории и парсинг с неё данных
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(category_url)

            # получаем все ссылки на товары
            product_links = page.locator("a.product-item")

            # перебираем все товары на странице категории
            for i in range(product_links.count()):
              product = product_links.nth(i)

              # получаем название товара
              product_name = product.inner_text().strip()

              # получаем ссылку на товар
              product_url = product.get_attribute("href")

              if product_url and product_url.startswith("/"):
                product_url = f"https://gosapteka.ru{product_url}"

              if product_name and product_url:
                await self.setProductToDataBase(product_name, product_url, category_name)

            browser.close()

        except Exception as e:
          print(f"Ошибка при парсинге категории {category_name}: {e}")


async def main():
    parser = First_Parsing_GosApteka()
    await parser.getProductsAtCategories()

if __name__ == "__main__":
  asyncio.run(main())
