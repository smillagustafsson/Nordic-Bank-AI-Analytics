import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# ---------------------------------------------------------
# 1. Load ML dataset
# ---------------------------------------------------------

file_path = (
    "data/generated/savings_ml_dataset.csv"
)

df = pd.read_csv(file_path)

print("Dataset loaded successfully.")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ---------------------------------------------------------
# 2. Select features and target
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

target = "will_reach_goal"

X = df[features]
y = df[target]


# ---------------------------------------------------------
# 3. Define numerical and categorical features
# ---------------------------------------------------------

numeric_features = [
    "age",
    "income",
    "target_amount",
    "current_amount",
    "days_to_target",
    "savings_progress",
    "remaining_amount",
    "required_monthly_saving",
    "required_saving_income_ratio"
]

categorical_features = [
    "risk_profile",
    "customer_segment"
]


# ---------------------------------------------------------
# 4. Prepare the data
# ---------------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            StandardScaler(),
            numeric_features
        ),
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ]
)


# ---------------------------------------------------------
# 5. Create ML pipeline
# ---------------------------------------------------------

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000
            )
        )
    ]
)


# ---------------------------------------------------------
# 6. Split data into training and test data
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print()
print(f"Training data: {len(X_train)}")
print(f"Test data: {len(X_test)}")


# ---------------------------------------------------------
# 7. Train the model
# ---------------------------------------------------------

print()
print("Training model...")

model.fit(
    X_train,
    y_train
)

print("Model training completed.")


# ---------------------------------------------------------
# 8. Examine model coefficients
# ---------------------------------------------------------

feature_names = model.named_steps[
    "preprocessor"
].get_feature_names_out()

coefficients = model.named_steps[
    "classifier"
].coef_[0]

feature_importance = pd.DataFrame({
    "feature": feature_names,
    "coefficient": coefficients
})

feature_importance["importance"] = (
    feature_importance["coefficient"].abs()
)

feature_importance = feature_importance.sort_values(
    "importance",
    ascending=False
)

print()
print("==========================================")
print("FEATURE IMPORTANCE")
print("==========================================")

print(
    feature_importance[
        [
            "feature",
            "coefficient",
            "importance"
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# 9. Make predictions
# ---------------------------------------------------------

y_pred = model.predict(
    X_test
)


# ---------------------------------------------------------
# 10. Evaluate the model
# ---------------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print()
print("==========================================")
print("MODEL RESULTS")
print("==========================================")

print(
    f"Accuracy: {accuracy:.2%}"
)

print()
print("Classification report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# ---------------------------------------------------------
# 11. Save trained model
# ---------------------------------------------------------

model_file = (
    "ai/savings_model.pkl"
)

joblib.dump(
    model,
    model_file
)

print()
print("==========================================")
print("MODEL SAVED")
print("==========================================")

print(
    f"Model saved to: {model_file}"
)