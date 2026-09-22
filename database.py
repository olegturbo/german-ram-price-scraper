import json 
import psycopg2
import os 

def save_products(products):
    connection = psycopg2.connect(
        host="localhost",
        port=os.environ.get("PORT", "5432"),
        database=os.environ.get("DATABASE"),
        user=os.environ.get("DB_USER", os.environ.get("USER")),
        password=os.environ.get("PASSWORD"),
    )

    cursor = connection.cursor()

    query = """
        INSERT INTO products(details)
        VALUES(%s)
    """

    for product in products:
        cursor.execute(
            query,
            (json.dumps(product, ensure_ascii=False),)
        )

    connection.commit()

    cursor.close()
    connection.close()