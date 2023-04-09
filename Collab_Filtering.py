import psycopg2.extras
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    database=os.getenv("postgres_DB"),
    host='localhost',
    port='5432',
    password=os.getenv("postgres_password"),
    user='postgres'
)
# Voor gemak cursor globaal gemaakt
cursor = conn.cursor()




def populaire_producten(sub_cat):

    # Hier kijkt of input False of True was waardoor die de categorie of subcategorie ophaald uit de database

    query = ""
    if sub_cat:
        query = ''' SELECT ord.productid, pro.sub_category
    FROM "order" as ord
    RIGHT JOIN product as pro ON ord.productid = pro.id'''
    else:
        query = ''' SELECT ord.productid, pro.category
    FROM "order" as ord
    RIGHT JOIN product as pro ON ord.productid = pro.id'''
    cursor.execute(query)

    all_orders_product = cursor.fetchall()


    frequency_table_product_per_category = {}

    # Print statement voor de duidelijkheid
    print("All orders frequentie tabel maken...")

    # In deze for loop haalt die uit de orders de best verkochte producten per categorie een
    # Voegt die ze toe aan een tabel
    for product in tqdm(all_orders_product):
        category = product[1]
        product_id = product[0]
        if product_id is None or category is None:
            continue
        category = category.lower()
        if frequency_table_product_per_category.get(category) is None:
            frequency_table_product_per_category[category] = {}

        frequency_table_product_per_category[category][product_id] = frequency_table_product_per_category[category].get(
            product_id, 0) + 1


    # Dictionary aanmaken
    top_4_products_per_category = {}


    # In deze voor loop haalt die de top 4 meest verkochte producten per categorie en voegt die toe aan de dictionary
    for categorie, producten in frequency_table_product_per_category.items():
        category_freq = frequency_table_product_per_category[categorie]
        top_products = sorted(category_freq, key=category_freq.get, reverse=True)[:4]

        top_4_products_per_category[categorie] = []
        for product_id in top_products:
            top_4_products_per_category[categorie].append(product_id)


    to_execute = []

    # Voor elke categorie voegt die de producten toe
    for category, products in top_4_products_per_category.items():
        for product_id in products:
            to_execute.append(product_id, category)

    # SQL query voor naar de database schrijven
    query = "INSERT INTO populaire_producten (productid, category) VALUES %s"

    to_execute = tuple(to_execute)

    psycopg2.extras.execute_values(cursor, query, to_execute)


