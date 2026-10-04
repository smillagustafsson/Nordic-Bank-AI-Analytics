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


# Hämta alla konton från databasen
with connection.cursor() as cursor:

    cursor.execute("""
        SELECT account_id
        FROM Account
    """)

    accounts = cursor.fetchall()


# Lista med transaktioner
transactions = []

# Transaktions-ID börjar på 1
transaction_id = 1


# Skapa transaktioner för varje konto
for (account_id,) in accounts:

    # Varje konto får mellan 10 och 50 transaktioner
    number_of_transactions = random.randint(10, 50)

    for _ in range(number_of_transactions):

        # Slumpa datum inom de senaste två åren
        days_ago = random.randint(0, 730)
        transaction_date = date.today() - timedelta(days=days_ago)

        # Slumpa om transaktionen är inkomst eller utgift
        transaction_type = random.choice([
            "Income",
            "Expense"
        ])

        # Slumpa kategori
        if transaction_type == "Income":

            category = random.choice([
                "Salary",
                "Transfer",
                "Interest"
            ])

            amount = round(
                random.uniform(1000, 50000),
                2
            )

        else:

            category = random.choice([
                "Food",
                "Shopping",
                "Housing",
                "Transport",
                "Bills",
                "Entertainment"
            ])

            amount = round(
                random.uniform(50, 5000),
                2
            )

        # Lägg till transaktionen
        transactions.append((
            transaction_id,
            account_id,
            transaction_date,
            amount,
            category,
            transaction_type
        ))

        transaction_id += 1


# Lägg in transaktionerna i PostgreSQL
with connection:

    with connection.cursor() as cursor:

        cursor.executemany(
            """
            INSERT INTO Transactions (
                transaction_id,
                account_id,
                transaction_date,
                amount,
                category,
                transaction_type
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            transactions
        )


# Stäng anslutningen
connection.close()


print(f"Successfully generated {len(transactions)} transactions.")