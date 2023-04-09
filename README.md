# README Business-Rules

### Collab Filtering uitleg

Deze code maakt gebruik van psycopg2 en tqdm om populaire producten per categorie of subcategorie te vinden en deze in een PostgreSQL-database te plaatsen.
De code maakt verbinding met de database met behulp van de gegevens in een .env-bestand en voert vervolgens een SQL-query uit om de nodige gegevens op te halen.
De code bouwt vervolgens een frequentietabel van de best verkochte producten per categorie en selecteert de top 4 producten per categorie.
De code voegt deze top 4-producten per categorie toe aan een dictionary en schrijft deze dictionary tenslotte naar de PostgreSQL-database met psycopg2.extras.execute_values.


### Content Filtering uitleg

Deze code maakt gebruik van de psycopg2.extras, tqdm en dotenv modules. 
De code maakt verbinding met de database en gebruikt de gegevens om aanbevelingen te doen aan klanten op basis van hun eerdere aankopen.
De functie 'categorie_aanbeveling(sub_cat)' accepteert een boolean parameter 'sub_cat' als input en retourneert een dictionary met als sleutel de ID van de klant en als waarde een dictionary van categorieën en aanbevolen producten. 
Als de parameter 'sub_cat' True is, worden subcategorieën gebruikt in plaats van categorieën om de aanbevelingen te maken.
De code begint met het maken van een frequentietabel van alle bestellingen per categorie (of subcategorie) om de best verkochte producten per categorie te bepalen. 
Vervolgens worden de profiel-ID's en product-ID's van alle profielen die eerder hebben gekocht uit de database gehaald.
Vervolgens wordt voor elk profiel gekeken naar de categorieën van de producten die ze eerder hebben gekocht en worden de aanbevolen producten toegevoegd op basis van de best verkochte producten in die categorie. 
Als er geen producten in de orders zijn voor een bepaalde categorie, worden er automatisch de top 4 meest verkochte producten in die categorie toegevoegd.
Tot slot worden alle aanbevelingen in een dictionary opgeslagen en naar de database geschreven.
