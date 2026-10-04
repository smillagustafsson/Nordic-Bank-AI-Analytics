import random
import getpass
from datetime import date, timedelta
import psycopg


# Fråga efter PostgreSQL-lösenord
password = getpass.getpass("Enter PostgreSQL password: ")


# Anslut till PostgreSQL
connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="nordic_bank",
    user="postgres",
    password=password
)


# Hämta alla kunder från databasen
with connection.cursor() as cursor:

    cursor.execute("""
        SELECT customer_id
        FROM Customer
    """)

    customers = cursor.fetchall()


# Svenska aktier och deras sektorer
stocks = {
    "SEB-A": "Bank/Finance",
    "SHB-A": "Bank/Finance",
    "SWED-A": "Bank/Finance",

    "VOLV-B": "Industrial",
    "SAND": "Industrial",
    "SKF-B": "Industrial",
    "SAAB-B": "Industrial",

    "ERIC-B": "Technology",
    "SINCH": "Technology",
    "HEXA-B": "Technology",

    "AZN": "Pharma/Healthcare",
    "SOBI": "Pharma/Healthcare",

    "HM-B": "Retail",
    "ELUX-B": "Retail",

    "CAST": "Real Estate",
    "FABG": "Real Estate",

    "TEL2-B": "Telecom",
    "TELIA": "Telecom",

    "INVE-B": "Investment Company",
    "KINV-B": "Investment Company",
    "LATO-B": "Investment Company"
}


# Lista med investeringar
investments = []

# Investment-ID börjar på 1
investment_id = 1


# Skapa investeringar för kunderna
for (customer_id,) in customers:

    # Alla kunder investerar inte
    invests = random.choice([
        True,
        True,
        True,
        False
    ])

    if not invests:
        continue

    # Varje investerande kund får 1–4 investeringar
    number_of_investments = random.randint(1, 4)

    for _ in range(number_of_investments):

        # Välj en aktie
        ticker = random.choice(list(stocks.keys()))

        # Hämta sektorn för aktien
        sector = stocks[ticker]

        # Tillgångstyp
        asset_type = "Stock"

        # Antal aktier
        quantity = round(
            random.uniform(1, 100),
            4
        )

        # Inköpspris
        purchase_price = round(
            random.uniform(50, 1000),
            2
        )

        # Slumpa inköpsdatum inom de senaste fem åren
        days_ago = random.randint(30, 1825)

        purchase_date = (
            date.today() - timedelta(days=days_ago)
        )

        # Lägg till investeringen
        investments.append((
            investment_id,
            customer_id,
            ticker,
            asset_type,
            sector,
            quantity,
            purchase_price,
            purchase_date
        ))

        investment_id += 1


# Lägg in investeringarna i PostgreSQL
with connection:

    with connection.cursor() as cursor:

        cursor.executemany(
            """
            INSERT INTO Investment (
                investment_id,
                customer_id,
                ticker,
                asset_type,
                sector,
                quantity,
                purchase_price,
                purchase_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            investments
        )


# Stäng anslutningen
connection.close()


print(f"Successfully generated {len(investments)} investments.")