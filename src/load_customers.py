import csv
import getpass
import psycopg


# Sökväg till CSV-filen
file_path = "Nordic-Bank-AI-Analytics/data/generated/customers.csv"


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


# Öppna CSV-filen
with open(file_path, "r", newline="", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    # Skapa en lista med kunder
    customers = []

    for row in reader:
        customers.append((
            int(row["customer_id"]),
            int(row["age"]),
            int(row["income"]),
            row["risk_profile"],
            row["customer_segment"]
        ))


# Lägg in kunderna i PostgreSQL
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


print(f"Successfully loaded {len(customers)} customers into PostgreSQL.")