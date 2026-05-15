# db_manager/db_manager.py
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
################# Ð’Ð½ÐµÑÐµÐ½Ð¸Ðµ Ð´Ð°Ð½Ð½Ñ‹Ñ… Ð² Ð±Ð´ ####################
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
            print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ…: {e}")

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
                    print(f"Ð¡ÑÑ‹Ð»ÐºÐ°: {product_url}, ÑƒÑÐ¿ÐµÑˆÐ½Ð¾ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½Ð°")
                    return cur.fetchall()

        except psycopg.Error as e:
            print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ… Ð¿Ñ€Ð¸ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½Ð¸Ð¸ Ñ‚Ð¾Ð²Ð°Ñ€Ð°: {e}")
            return None

    def insert_medecines_info(self, name, normalize_name, description, manufacturer, image_url):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO medcines (name, normalize_name, description, manufacturer, image_url)
                        VALUES(%s, %s, %s, %s, %s)
                        RETURING id
                        """,
                        (name, normalize_name, description, manufacturer, image_url)
                    )

        except psycopg.Error as e:
            print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð¿Ñ€Ð¸ Ð²Ð½ÐµÐ½ÐµÐ½Ð¸Ð¸ Ð´Ð°Ð½Ð½Ñ‹Ñ… Ð¿Ð¾ Ð»ÐµÐºÐ°Ñ€ÑÑ‚Ð²Ñƒ Ð² Ð±Ð´: {e}")

    def isert_price_info(self, price, pharmancys_id, medecines_id, date_parse, medecine_url):
        try:
            with psycopg.connect(self.conninfo) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO medcines (price, pharmancys_id, medecines_id, date_parse, medecine_url)
                        VALUES(%s, %s, %s, %s, %s)
                        RETURING id
                        """,
                        (price, pharmancys_id, medecines_id, date_parse, medecine_url)
                    )

        except psycopg.Error as e:
            print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð¿Ñ€Ð¸ Ð²Ð½ÐµÐ½ÐµÐ½Ð¸Ð¸ Ð´Ð°Ð½Ð½Ñ‹Ñ… Ð¿Ð¾ Ñ†ÐµÐ½Ðµ Ð² Ð±Ð´: {e}")
################# ÐŸÐ¾Ð»ÑƒÑ‡ÐµÐ½Ð¸Ðµ Ð´Ð°Ð½Ð½Ñ‹Ñ… Ð¸Ð· Ð±Ð´ ####################
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
            print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð¸Ñ Ñ‚Ð¾Ð²Ð°Ñ€Ð¾Ð² Ð¸Ð· Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ…: {e}")

    def get_categories(self, pharmacy_id):
        try:
            with psycopg.connect(self.conninfo) as conn:
                print("Ð£ÑÐ¿ÐµÑˆÐ½Ð¾Ðµ Ð¿Ð¾Ð´ÐºÐ»ÑŽÑ‡ÐµÐ½Ð¸Ðµ Ðº Ð±Ð°Ð·Ðµ Ð´Ð°Ð½Ð½Ñ‹Ñ…")
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
            print(f"ÐžÑˆÐ¸Ð±ÐºÐ° Ð±Ð°Ð·Ñ‹ Ð´Ð°Ð½Ð½Ñ‹Ñ…: {e}")
            return []
