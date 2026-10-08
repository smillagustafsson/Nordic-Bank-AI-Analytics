import random
import getpass
import psycopg


# Antal kunder vi vill skapa
NUMBER_OF_CUSTOMERS = 1000


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


# Skapa kunder
customers = []

for customer_id in range(1, NUMBER_OF_CUSTOMERS + 1):

    # Slumpa ålder mellan 20 och 70
    age = random.randint(20, 70)

    # Slumpa inkomst mellan 25 000 och 80 000 kr
    income = random.randint(25000, 80000)

    # Slumpa riskprofil
    risk_profile = random.choice([
        "Low",
        "Medium",
        "High"
    ])

    # Bestäm kundsegment utifrån ålder
    if age <= 30:
        customer_segment = "Young Professional"
    elif age <= 45:
        customer_segment = "Established Professional"
    else:
        customer_segment = "Mature Customer"

    customers.append((
        customer_id,
        age,
        income,
        risk_profile,
        customer_segment
    ))


# Lägg in kunderna direkt i PostgreSQL
with connection:

    with connection.cursor() as cursor:

        cursor.executemany(
            """
            INSERT INTO Customer (
                customer_id,
                age,
                income,
                risk_profile,
                customer_segment
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            customers
        )


# Stäng anslutningen
connection.close()


print(f"Successfully generated and loaded {len(customers)} customers into PostgreSQL.")