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
        SELECT customer_id, income
        FROM Customer
    """)

    customers = cursor.fetchall()


# Lista med konton
accounts = []

# Konto-ID börjar på 1
account_id = 1


# Skapa 1–3 konton per kund
for customer_id, income in customers:

    income = float(income)

    number_of_accounts = random.randint(1, 3)

    for _ in range(number_of_accounts):

        # Slumpa kontotyp
        account_type = random.choice([
            "Checking",
            "Savings",
            "Investment"
        ])

        # Skapa ett saldo baserat på kundens inkomst
        balance = round(
            random.uniform(income * 0.2, income * 8),
            2
        )

        # Slumpa öppningsdatum
        days_ago = random.randint(30, 3650)
        opened_date = date.today() - timedelta(days=days_ago)

        # Lägg till kontot
        accounts.append((
            account_id,
            customer_id,
            account_type,
            balance,
            opened_date
        ))

        account_id += 1


# Lägg in kontona i PostgreSQL
with connection:

    with connection.cursor() as cursor:

        cursor.executemany(
            """
            INSERT INTO Account (
                account_id,
                customer_id,
                account_type,
                balance,
                opened_date
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            accounts
        )


# Stäng anslutningen
connection.close()


print(f"Successfully generated {len(accounts)} accounts.")