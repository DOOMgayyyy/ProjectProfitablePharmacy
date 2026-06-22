import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv


class DatabaseManager:
    """
    * Конструктор класса для подключения к базе данных
    * Загружает переменные окружения из .env
    * Проверяет наличие обязательных переменных и формирует строку подключения
    """
    def __init__(self):
        current_file = Path(__file__).resolve()
        env_path = current_file.parents[3] / ".env"

        load_dotenv(dotenv_path=env_path)

        db_url = os.getenv("DB_URL")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")

        if not all([db_url, db_port, db_name, db_user, db_pass]):
            raise ValueError(
                f"Не найдены переменные окружения для БД. "
                f"Проверь файл .env по пути: {env_path}"
            )

        self.conninfo = (
            f"host={db_url} "
            f"port={db_port} "
            f"dbname={db_name} "
            f"user={db_user} "
            f"password={db_pass}"
        )

    ################# Внесение данных в бд ####################

    """
    * Функция для добавления категории в базу данных
    * @param category_name - название категории
    * @param category_url - ссылка на категорию
    * @param pharmacy_id - id аптеки
    """
    def insert_category(self, category_name, category_url, pharmacy_id):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO categories (category_name, categories_url, pharmacy_id)
                        VALUES (%s, %s, %s)
                        """,
                        (category_name, category_url, pharmacy_id)
                    )
                conn.commit()
        except psycopg.Error as e:
            print(f"Ошибка базы данных: {e}")

    """
    * Функция для добавления ссылки на товар в таблицу medicines
    * @param product_url - ссылка на товар
    * @param category_id - id категории
    * @return id добавленного товара или None в случае ошибки
    """
    def insert_url_to_medicines(self, product_url, category_id):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO medicines (product_url, category_id)
                        VALUES (%s, %s)
                        RETURNING id
                        """,
                        (product_url, category_id)
                    )
                    row = cur.fetchone()
                    conn.commit()
                    print(f"Ссылка: {product_url}, успешно добавлена")
                    return row[0] if row else None

        except psycopg.Error as e:
            print(f"Ошибка базы данных при добавлении товара: {e}")
            return None

    """
    * Функция для добавления информации о цене лекарства в таблицу prices
    * @param price - цена лекарства
    * @param pharmacy_id - id аптеки
    * @param medicine_id - id лекарства
    * @param date_parse - дата парсинга
    * @param medicine_url - ссылка на страницу лекарства
    * @return id добавленной цены или None в случае ошибки
    """
    def insert_price_info(self, price, pharmacy_id, medicine_id, date_parse, medicine_url):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO prices (price, pharmacy_id, medicine_id, date_parse, medicine_url)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (price, pharmacy_id, medicine_id, date_parse, medicine_url),
                    )
                    row = cur.fetchone()
                    conn.commit()

            if row is None:
                print("WARNING: INSERT INTO prices вернул None в fetchone()")
                return None

            return row[0]

        except psycopg.Error as e:
            print(f"Ошибка при внесении данных по цене в бд: {e}")
            return None

    ################# Получение данных из бд ####################

    """
    * Функция для получения всех ссылок на товары из таблицы medicines
    * @return список кортежей (id, product_url)
    """
    def get_url_at_products(self):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, product_url
                        FROM medicines
                        """
                    )
                    return cur.fetchall()
        except psycopg.Error as e:
            print(f"Ошибка получения товаров из базы данных: {e}")
            return []

    """
    * Функция для получения всех категорий по id аптеки
    * @param pharmacy_id - id аптеки
    * @return список кортежей (id, categories_url)
    """
    def get_categories(self, pharmacy_id):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, categories_url
                        FROM categories
                        WHERE pharmacy_id = %s
                        """,
                        (pharmacy_id,)
                    )
                    return cur.fetchall()
        except psycopg.Error as e:
            print(f"Ошибка базы данных: {e}")
            return []

    """
    * Функция для получения уникальных ссылок на товары из таблицы prices по id аптеки
    * Используется в reParsers для обхода только тех URL, которые уже были спаршены
    * @param pharmacy_id - id аптеки
    * @return список кортежей (price_id, medicine_id, medicine_url)
    """
    def get_urls_from_prices(self, pharmacy_id):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT DISTINCT ON (medicine_url)
                            id,
                            medicine_id,
                            medicine_url
                        FROM prices
                        WHERE pharmacy_id = %s
                          AND medicine_url IS NOT NULL
                        ORDER BY medicine_url, date_parse DESC
                        """,
                        (pharmacy_id,)
                    )
                    return cur.fetchall()
        except psycopg.Error as e:
            print(f"Ошибка получения URL из prices: {e}")
            return []

    """
    * Функция для поиска лекарства по нормализованному имени с помощью trigram similarity
    * Используется для поиска наиболее похожего лекарства в таблице medicines
    * @param normalize_name - нормализованное название лекарства
    * @param min_similarity - минимальный порог схожести названий
    * @return словарь с данными найденного лекарства или None, если совпадение не найдено
    """
    def get_medicine_by_trgm_name(self, normalize_name, min_similarity=0.40):
        if not normalize_name:
            return None

        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id,
                               name,
                               normalize_name,
                               similarity(normalize_name, %s) AS sim
                        FROM medicines
                        WHERE normalize_name IS NOT NULL
                          AND similarity(normalize_name, %s) >= %s
                        ORDER BY sim DESC
                        LIMIT 1
                        """,
                        (normalize_name, normalize_name, min_similarity)
                    )
                    row = cur.fetchone()

                    if row:
                        return {
                            "id": row[0],
                            "name": row[1],
                            "normalize_name": row[2],
                            "similarity": row[3],
                        }

                    return None

        except psycopg.Error as e:
            print(f"Ошибка trigram-поиска лекарства: {e}")
            return None

    ##################### Обновление записей ####################

    """
    * Функция для обновления информации о лекарстве в таблице medicines
    * @param medicine_id - id лекарства
    * @param name - название лекарства
    * @param normalize_name - нормализованное название
    * @param description - описание лекарства
    * @param manufacturer - производитель лекарства
    * @param image_url - ссылка на изображение
    """
    def update_medicine_info(self, medicine_id, name, normalize_name, description, manufacturer, image_url):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE medicines
                        SET
                            name = %s,
                            normalize_name = %s,
                            description = %s,
                            manufacturer = %s,
                            image_url = %s
                        WHERE id = %s
                        """,
                        (name, normalize_name, description, manufacturer, image_url, medicine_id)
                    )
                    conn.commit()
        except psycopg.Error as e:
            print(f"Ошибка при обновлении данных по лекарству в бд: {e}")

    """
    * Функция для обновления цены в таблице prices по id записи
    * Используется в reParsers для актуализации цен без создания новой записи
    * @param price_id - id записи в таблице prices
    * @param new_price - новая цена
    * @param new_date - новая дата парсинга (datetime.date)
    """
    def update_price(self, price_id, new_price, new_date):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE prices
                        SET
                            price = %s,
                            date_parse = %s
                        WHERE id = %s
                        """,
                        (new_price, new_date, price_id)
                    )
                    conn.commit()
        except psycopg.Error as e:
            print(f"Ошибка при обновлении цены (id={price_id}): {e}")

    ##################### Удаление записей ####################

    """
    * Функция для удаления всех записей из таблицы medicines
    * @return количество удалённых строк или 0 в случае ошибки
    """
    def delete_all_medecines(self):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        DELETE FROM medicines
                        """
                    )
                    conn.commit()
                    return cur.rowcount
        except psycopg.Error as e:
            print(f"Ошибка базы данных: {e}")
            return 0
