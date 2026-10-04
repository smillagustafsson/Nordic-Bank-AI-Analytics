import pandas as pd
import joblib


# ---------------------------------------------------------
# 1. Load the trained model
# ---------------------------------------------------------

model_file = (
    "ai/savings_model.pkl"
)

model = joblib.load(model_file)


# ---------------------------------------------------------
# 2. Load the ML dataset
# ---------------------------------------------------------

data_file = (
    "data/generated/savings_ml_dataset.csv"
)

df = pd.read_csv(data_file)


# ---------------------------------------------------------
# 3. Ask for a customer ID
# ---------------------------------------------------------

customer_id = int(
    input("Enter customer ID: ")
)


# ---------------------------------------------------------
# 4. Find the customer
# ---------------------------------------------------------

customer = df[
    df["customer_id"] == customer_id
]


# ---------------------------------------------------------
# 5. Check if the customer exists
# ---------------------------------------------------------

if customer.empty:
    print()
    print("Customer not found.")
    exit()


# ---------------------------------------------------------
# 6. Select the features used by the model
# ---------------------------------------------------------

features = [
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
    "required_saving_income_ratio"
]

X_customer = customer[
    features
]


# ---------------------------------------------------------
# 7. Make a prediction
# ---------------------------------------------------------

prediction = model.predict(
    X_customer
)[0]


# ---------------------------------------------------------
# 8. Calculate prediction probabilities
# ---------------------------------------------------------

probabilities = model.predict_proba(
    X_customer
)[0]

probability_not_reach = probabilities[0]
probability_reach = probabilities[1]


# ---------------------------------------------------------
# 9. Get customer information
# ---------------------------------------------------------

current_savings = customer[
    "current_amount"
].iloc[0]

target_amount = customer[
    "target_amount"
].iloc[0]

savings_progress = customer[
    "savings_progress"
].iloc[0]

days_to_target = customer[
    "days_to_target"
].iloc[0]

income = customer[
    "income"
].iloc[0]

risk_profile = customer[
    "risk_profile"
].iloc[0]

customer_segment = customer[
    "customer_segment"
].iloc[0]

remaining_amount = customer[
    "remaining_amount"
].iloc[0]

required_monthly_saving = customer[
    "required_monthly_saving"
].iloc[0]

required_saving_income_ratio = customer[
    "required_saving_income_ratio"
].iloc[0]


# ---------------------------------------------------------
# 10. Display customer information
# ---------------------------------------------------------

print()
print("==========================================")
print("NORDIC BANK")
print("SAVINGS GOAL PREDICTION")
print("==========================================")

print()

print(f"Customer ID: {customer_id}")
print(f"Customer segment: {customer_segment}")
print(f"Risk profile: {risk_profile}")
print(f"Income: {income:,.0f} kr")

print()

print(f"Current savings: {current_savings:,.0f} kr")
print(f"Target amount: {target_amount:,.0f} kr")
print(f"Savings progress: {savings_progress:.1%}")
print(f"Remaining amount: {remaining_amount:,.0f} kr")
print(f"Days to target: {days_to_target}")
print(
    f"Required monthly saving: "
    f"{required_monthly_saving:,.0f} kr"
)

print()


# ---------------------------------------------------------
# 11. Display prediction
# ---------------------------------------------------------

print("------------------------------------------")

if prediction == 1:
    print("Prediction: LOW RISK")
else:
    print("Prediction: HIGH RISK")

print("------------------------------------------")

print()

print(
    f"Probability of reaching goal: "
    f"{probability_reach:.1%}"
)

print(
    f"Probability of not reaching goal: "
    f"{probability_not_reach:.1%}"
)


# ---------------------------------------------------------
# 12. Create an explanation
# ---------------------------------------------------------

print()
print("==========================================")
print("PREDICTION EXPLANATION")
print("==========================================")

if prediction == 0:

    print()
    print("The model predicts a higher risk of")
    print("not reaching the savings goal.")

    print()
    print("Relevant customer indicators:")

    if savings_progress < 0.25:
        print(
            f"- Savings progress is relatively low "
            f"({savings_progress:.1%})."
        )

    if remaining_amount > target_amount * 0.50:
        print(
            f"- A large part of the goal remains "
            f"({remaining_amount:,.0f} kr)."
        )

    if days_to_target < 730:
        print(
            f"- The customer has {days_to_target} days "
            f"remaining to reach the target."
        )

    if required_saving_income_ratio > 0.20:
        print(
            f"- The required monthly saving represents "
            f"{required_saving_income_ratio:.1%} "
            f"of the customer's income."
        )

else:

    print()
    print("The model predicts a lower risk of")
    print("not reaching the savings goal.")

    print()
    print("Relevant customer indicators:")

    if savings_progress >= 0.50:
        print(
            f"- The customer has already saved "
            f"{savings_progress:.1%} of the goal."
        )

    if days_to_target >= 730:
        print(
            f"- The customer has {days_to_target} days "
            f"remaining to reach the target."
        )

    if required_saving_income_ratio <= 0.20:
        print(
            f"- The required monthly saving represents "
            f"{required_saving_income_ratio:.1%} "
            f"of the customer's income."
        )

    if remaining_amount <= target_amount * 0.50:
        print(
            f"- Less than half of the target remains "
            f"({remaining_amount:,.0f} kr)."
        )


print()
print("==========================================")