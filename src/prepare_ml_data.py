import pandas as pd
import psycopg
import getpass
import os


# ---------------------------------------------------------
# 1. Connect to PostgreSQL
# ---------------------------------------------------------

password = getpass.getpass("Enter PostgreSQL password: ")

connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="nordic_bank",
    user="postgres",
    password=password
)


# ---------------------------------------------------------
# 2. Load customer and savings goal data
# ---------------------------------------------------------

query = """
SELECT
    c.customer_id,
    c.age,
    c.income,
    c.risk_profile,
    c.customer_segment,

    s.goal_id,
    s.goal_name,
    s.target_amount,
    s.current_amount,
    s.target_date

FROM Customer c

JOIN SavingsGoal s
    ON c.customer_id = s.customer_id;
"""


df = pd.read_sql(query, connection)

connection.close()


# ---------------------------------------------------------
# 3. Convert dates
# ---------------------------------------------------------

df["target_date"] = pd.to_datetime(df["target_date"])

today = pd.Timestamp.today().normalize()

df["days_to_target"] = (
    df["target_date"] - today
).dt.days


# ---------------------------------------------------------
# 4. Create savings progress
# ---------------------------------------------------------

df["savings_progress"] = (
    df["current_amount"] / df["target_amount"]
)


# Avoid values above 100%
df["savings_progress"] = df["savings_progress"].clip(
    lower=0,
    upper=1
)


# ---------------------------------------------------------
# 5. Calculate remaining amount
# ---------------------------------------------------------

df["remaining_amount"] = (
    df["target_amount"] - df["current_amount"]
)

df["remaining_amount"] = df["remaining_amount"].clip(
    lower=0
)


# ---------------------------------------------------------
# 6. Calculate required monthly savings
# ---------------------------------------------------------

months_remaining = (
    df["days_to_target"] / 30.44
)

months_remaining = months_remaining.clip(
    lower=1
)

df["required_monthly_saving"] = (
    df["remaining_amount"] / months_remaining
)


# ---------------------------------------------------------
# 7. Calculate required saving as percentage of income
# ---------------------------------------------------------

df["required_saving_income_ratio"] = (
    df["required_monthly_saving"] / df["income"]
)


# ---------------------------------------------------------
# 8. Create a synthetic target variable
#
# 1 = likely to reach savings goal
# 0 = unlikely to reach savings goal
#
# This is NOT real historical bank data.
# It is a synthetic outcome created for the ML portfolio project.
# ---------------------------------------------------------

df["will_reach_goal"] = (
    (
        (df["savings_progress"] >= 0.50)
        |
        (
            df["required_saving_income_ratio"] <= 0.20
        )
    )
).astype(int)


# ---------------------------------------------------------
# 9. Create a simpler risk label
# ---------------------------------------------------------

df["goal_risk"] = df["will_reach_goal"].map({
    1: "Low",
    0: "High"
})


# ---------------------------------------------------------
# 10. Select columns for machine learning
# ---------------------------------------------------------

ml_data = df[
    [
        "customer_id",
        "age",
        "income",
        "risk_profile",
        "customer_segment",
        "target_amount",
        "current_amount",
        "days_to_target",
        "savings_progress",
        "remaining_amount",
        "required_monthly_saving",
        "required_saving_income_ratio",
        "will_reach_goal",
        "goal_risk"
    ]
].copy()


# ---------------------------------------------------------
# 11. Remove invalid rows
# ---------------------------------------------------------

ml_data = ml_data.dropna()


# ---------------------------------------------------------
# 12. Create output folder
# ---------------------------------------------------------

output_folder = "Nordic-Bank-AI-Analytics/data/generated"

os.makedirs(
    output_folder,
    exist_ok=True
)


# ---------------------------------------------------------
# 13. Save ML dataset
# ---------------------------------------------------------

output_file = (
    f"{output_folder}/"
    "savings_ml_dataset.csv"
)

ml_data.to_csv(
    output_file,
    index=False
)


# ---------------------------------------------------------
# 14. Display information
# ---------------------------------------------------------

print()
print("==========================================")
print("ML DATASET CREATED")
print("==========================================")

print(f"Rows: {len(ml_data)}")
print(f"Columns: {len(ml_data.columns)}")

print()
print("Columns:")
for column in ml_data.columns:
    print(f"- {column}")

print()
print("Target distribution:")
print(
    ml_data["will_reach_goal"]
    .value_counts()
    .sort_index()
)

print()
print(f"Dataset saved to:")
print(output_file)

print()
print("First 5 rows:")
print(ml_data.head())