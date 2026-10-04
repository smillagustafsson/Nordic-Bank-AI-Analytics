import random
import csv

# Antal kunder vi vill skapa
NUMBER_OF_CUSTOMERS = 1000

# Lista som ska innehålla alla kunder
customers = []

# Skapa kunder
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

    # Lägg till kunden i listan
    customers.append({
        "customer_id": customer_id,
        "age": age,
        "income": income,
        "risk_profile": risk_profile,
        "customer_segment": customer_segment
    })


# Sökväg till CSV-filen
file_path = "Nordic-Bank-AI-Analytics/data/generated/customers.csv"

# Spara kunderna som CSV
with open(file_path, "w", newline="", encoding="utf-8") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "customer_id",
            "age",
            "income",
            "risk_profile",
            "customer_segment"
        ]
    )

    # Skriver rubrikerna
    writer.writeheader()

    # Skriver alla kunder
    writer.writerows(customers)


print(f"{NUMBER_OF_CUSTOMERS} customers generated!")
print(f"Saved to: {file_path}")