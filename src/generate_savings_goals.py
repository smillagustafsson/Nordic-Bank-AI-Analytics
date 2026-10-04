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


# Olika typer av sparmål
goal_names = [
    "Emergency Fund",
    "Travel",
    "House",
    "Car",
    "Education",
    "Retirement"
]


# Lista med sparmål
savings_goals = []

# Goal-ID börjar på 1
goal_id = 1


# Skapa sparmål för kunderna
for customer_id, income in customers:

    # Alla kunder har inte ett sparmål
    has_goal = random.choice([
        True,
        True,
        True,
        False
    ])

    if not has_goal:
        continue

    # 1–2 sparmål per kund
    number_of_goals = random.randint(1, 2)

    for _ in range(number_of_goals):

        # Välj typ av sparmål
        goal_name = random.choice(goal_names)

        # Skapa ett målbelopp baserat på inkomsten
        target_amount = round(
            random.uniform(
                float(income) * 2,
                float(income) * 12
            ),
            2
        )

        # Hur mycket kunden redan har sparat
        current_amount = round(
            random.uniform(
                0,
                target_amount
            ),
            2
        )

        # Slumpa måldatum inom 6 månader till 5 år
        days_ahead = random.randint(180, 1825)

        target_date = (
            date.today() + timedelta(days=days_ahead)
        )

        # Lägg till sparmålet
        savings_goals.append((
            goal_id,
            customer_id,
            goal_name,
            target_amount,
            current_amount,
            target_date
        ))

        goal_id += 1


# Lägg in sparmålen i PostgreSQL
with connection:

    with connection.cursor() as cursor:

        cursor.executemany(
            """
            INSERT INTO SavingsGoal (
                goal_id,
                customer_id,
                goal_name,
                target_amount,
                current_amount,
                target_date
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            savings_goals
        )


# Stäng anslutningen
connection.close()


print(f"Successfully generated {len(savings_goals)} savings goals.")