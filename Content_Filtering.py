import psycopg2.extras
from tqdm import tqdm
from dotenv import load_dotenv
import os

conn = psycopg2.connect(
    database=os.getenv("postgres_DB"),
    host='localhost',
    port='5432',
    password=os.getenv("postgres_password"),
    user='postgres'
)
# Voor gemak cursor globaal gemaakt
cursor = conn.cursor()


def categorie_aanbeveling(sub_cat):

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


    # Print statement voor duidelijkheid
    print("Data uit database halen...")

    # Haalt alle profile ids en product ids van de database
    cursor.execute(f'''SELECT prof.id, ord.productid
    FROM profile as prof
    RIGHT JOIN session as ses ON ses.profileid = prof.id AND has_sale = true
    RIGHT JOIN "order" as ord ON ses.id = ord.sessionid''')

    alle_profile_ids_en_product_ids = cursor.fetchall()

    # Print statement voor duidelijkheid
    print("Profiel connecten met producten...")

    # Dictionary aanmaken
    profile_dict = {}

    # In deze for loop kijkt die naar de gekochten per profiel
    # En voegt die gekochte producten toevoegt aan het profiel
    for profile, product in tqdm(alle_profile_ids_en_product_ids):
        if profile in profile_dict:
            profile_dict[profile].append(product)
        else:
            profile_dict[profile] = [product]

    # Hier kijkt of input False of True was waardoor die de categorie of subcategorie ophaald uit de database
    query = ""
    if sub_cat:
        query = '''
    SELECT id,sub_category
    FROM product'''
    else:
        query ='''
    SELECT id,category
    FROM product
    '''
    cursor.execute(query)

    aanbeveling = {}
    print("Aanbevelingen maken voorbereiden...")
    producten = cursor.fetchall()
    for product in producten:
        categorie = None
        if product[1]:
            categorie = product[1]

        if categorie and product[0]:
            categorie = categorie.lower()
            if categorie not in aanbeveling:
                aanbeveling[categorie] = []
            aanbeveling[categorie].append(product[0])

    # Dictionay aanmaken
    result_dict = {}

    # In deze for loop kijkt die per profiel de gekochte producten in de bijbehorende categorie horen
    # En daarna voegt hij die toe
    for profile, products in tqdm(profile_dict.items()):
        result_dict[profile] = {}
        for category in aanbeveling:
            result_dict[profile][category] = []
            for product_id in products:
                if str(product_id) in aanbeveling[category]:
                    result_dict[profile][category].append(product_id)


    # Print statement voor duidelijkheid wat er gebeurd
    print("Aanbevelingen maken...")

    # In deze for loop kijk ik voor elk profiel of er producten zijn gekocht in een categorie en
    # Als er geen producten in de orders zijn voegt hij producten toe die populair zijn in die categorie
    for profile in tqdm(result_dict):
        for category in top_4_products_per_category:

            if category not in result_dict[profile]:
                result_dict[profile][category] = []

            for product in top_4_products_per_category[category]:

                if len(result_dict[profile][category]) < 4:
                    result_dict[profile][category].append(product)


    # In deze for loop kijkt die als er meer dan 4 producten in een categorie zijn gekocht
    # dat hij er maximaal 4 van maakt
    for profile in result_dict:
        for category in result_dict[profile]:
            if len(result_dict[profile][category]) > 4:
                result_dict[profile][category] = result_dict[profile][category][:4]



    # In deze for loop kijkt hij of er 4 producten per categorie worden aanbevolen en anders voegt hij die toe
    for profile in tqdm(result_dict):
        for category in top_4_products_per_category:
            if category not in result_dict[profile]:
                result_dict[profile][category] = []

            # Als er nog niet genoeg producten in de categorie zit voegt die producten
            # Vanuit de dictionary met alle producten per categorie
            if len(result_dict[profile][category]) < 4:
                for product_id in aanbeveling.get(category, []):
                    if len(result_dict[profile][category]) >= 4:
                        break
                    if product_id not in result_dict[profile][category]:
                        result_dict[profile][category].append(product_id)

    # Print statement voor duidelijkheid
    print("Data voorbereiden voor database...")

    # Hier voeg ik elk profiel en de bijborende producten toe aan de database
    to_execute = []
    for profile_id, categories in tqdm(result_dict.items()):
        for category, products in categories.items():
            for product in products:
                to_execute.append((profile_id, product, category))


    # Hier voeg ik het toe als de gebruiker geen profiel heeft

    for category, products in top_4_products_per_category.items():
        profile_id = None
        for product in products:
            to_execute.append((profile_id, product, category))

    # SQL query voor het toevoegen
    query = "INSERT INTO meest_gekocht (profileid, productid, category) VALUES %s"

    to_execute = tuple(to_execute)

    # Print statement voor duidelijkheid
    print(f"{len(to_execute)} aanbeveling_categorie tabellen maken...")
    psycopg2.extras.execute_values(cursor, query, to_execute)