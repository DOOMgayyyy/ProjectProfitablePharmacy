import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv
class DatabaseManager:
    def __init__(self):
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(env_path)
        self.conninfo = (
            f"host={os.getenv('DB_URL')} "
            f"port={os.getenv('DB_PORT')} "
            f"dbname={os.getenv('DB_NAME')} "
            f"user={os.getenv('DB_USER')} "
            f"password={os.getenv('DB_PASS')}"
        )
################# InsertToDataBase ####################
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
                    print(f"Ссылка: {product_url}, успешно добавлена")
                    return cur.fetchall()

        except psycopg.Error as e:
            print(f"Ошибка базы данных при добавлении товара: {e}")
            return None

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
                # на всякий случай лог
                print("WARNING: INSERT INTO prices вернул None в fetchone()")
                return None

            price_id = row[0]
            return price_id

        except psycopg.Error as e:
            print(f"Ошибка при внесении данных по цене в бд: {e}")
            return None
################# Получение данных из бд ####################
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

    def get_categories(self, pharmacy_id):
        try:
            with psycopg.connect(self.conninfo) as conn:
                print("Успешное подключение к базе данных")
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
#####Обновление записей в базе данных######
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



##################### Удалить все записи ####################################
    def delete_all_medecines(self):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                    """
                    DELETE FROM medicines
                    """,
                    )
                    return cur.rowcount
        except psycopg.Error as e:
            print(f"Ошибка базы данных: {e}")
            return []
