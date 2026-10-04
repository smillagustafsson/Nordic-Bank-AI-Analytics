import json
import joblib
import pandas as pd
import ollama


from database_connection import (
    get_customer_from_database,
    get_savings_goal_from_database,
    get_accounts_from_database,
    get_transactions_from_database,
    get_investments_from_database,
    get_market_data_from_database,
    get_all_customers_from_database,
    get_all_savings_goals_from_database,
    get_all_accounts_from_database,
    get_all_transactions_from_database,
    get_all_investments_from_database
)


# ============================================================
# SETTINGS
# ============================================================

MODEL_NAME = "llama3.2:3b"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def convert_value(value):
    """
    Converts PostgreSQL values such as Decimal and dates
    into values that can be sent to the LLM as JSON.
    """

    if hasattr(value, "isoformat"):
        return value.isoformat()

    if hasattr(value, "__float__"):
        return float(value)

    return value


def convert_rows(rows, columns):
    """
    Converts database rows into dictionaries.
    """

    result = []

    for row in rows:
        item = {}

        for column, value in zip(columns, row):
            item[column] = convert_value(value)

        result.append(item)

    return result


def validate_customer_id(customer_id):
    """
    Makes sure that the customer ID is a valid integer.
    """

    try:
        return int(customer_id)

    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid customer ID: {customer_id}"
        )


# ============================================================
# DATABASE TOOLS
# ============================================================

def get_customer(customer_id):
    """
    Retrieves basic information about a customer.
    """

    customer_id = validate_customer_id(customer_id)

    customer = get_customer_from_database(
        customer_id
    )

    if customer is None:
        return {
            "error": (
                f"Customer {customer_id} "
                "was not found."
            )
        }

    return {
        "customer_id": int(
            customer["customer_id"]
        ),
        "age": int(
            customer["age"]
        ),
        "income": float(
            customer["income"]
        ),
        "risk_profile": customer[
            "risk_profile"
        ],
        "customer_segment": customer[
            "customer_segment"
        ]
    }


def get_savings_goals(customer_id):
    """
    Retrieves savings goals for a customer.
    """

    customer_id = validate_customer_id(
        customer_id
    )

    goals = get_savings_goal_from_database(
        customer_id
    )

    columns = [
        "goal_id",
        "customer_id",
        "goal_name",
        "target_amount",
        "current_amount",
        "target_date"
    ]

    return convert_rows(
        goals,
        columns
    )


def get_accounts(customer_id):
    """
    Retrieves bank accounts for a customer.
    """

    customer_id = validate_customer_id(
        customer_id
    )

    accounts = get_accounts_from_database(
        customer_id
    )

    columns = [
        "account_id",
        "customer_id",
        "account_type",
        "balance",
        "opened_date"
    ]

    return convert_rows(
        accounts,
        columns
    )


# ============================================================
# TRANSACTIONS
# ============================================================

def get_transactions(customer_id):
    """
    Retrieves transaction records for a customer.
    """

    customer_id = validate_customer_id(
        customer_id
    )

    transactions = (
        get_transactions_from_database(
            customer_id
        )
    )

    columns = [
        "transaction_id",
        "account_id",
        "transaction_date",
        "amount",
        "category",
        "transaction_type"
    ]

    transaction_data = convert_rows(
        transactions,
        columns
    )

    formatted_transactions = []

    for transaction in transaction_data:

        formatted_transactions.append({
            "date":
                transaction["transaction_date"],

            "amount":
                transaction["amount"],

            "category":
                transaction["category"],

            "transaction_type":
                transaction["transaction_type"]
        })

    return {
        "customer_id":
            customer_id,

        "transaction_count":
            len(formatted_transactions),

        "transactions":
            formatted_transactions
    }


def get_investments(customer_id):
    """
    Retrieves investments for a customer.
    """

    customer_id = validate_customer_id(
        customer_id
    )

    investments = (
        get_investments_from_database(
            customer_id
        )
    )

    columns = [
        "investment_id",
        "customer_id",
        "ticker",
        "asset_type",
        "sector",
        "quantity",
        "purchase_price",
        "purchase_date"
    ]

    return convert_rows(
        investments,
        columns
    )


def get_customer_financial_overview(
    customer_id
):
    """
    Combines customer, savings, account and
    investment information for a customer.

    This tool is useful when a question requires
    information from multiple database tables.
    """

    customer_id = validate_customer_id(
        customer_id
    )

    customer = get_customer(
        customer_id
    )

    savings_goals = get_savings_goals(
        customer_id
    )

    accounts = get_accounts(
        customer_id
    )

    investments = get_investments(
        customer_id
    )

    # Calculate total account balance
    total_account_balance = sum(
        account["balance"]
        for account in accounts
    )

    # Calculate investment value based on
    # quantity x purchase price
    total_investment_value = sum(
        investment["quantity"]
        * investment["purchase_price"]
        for investment in investments
    )

    # Calculate comparison between accounts
    # and investments
    if total_investment_value > 0:

        account_to_investment_ratio = (
            total_account_balance
            / total_investment_value
        )

    else:

        account_to_investment_ratio = None

    return {
        "customer": customer,

        "savings_goals": savings_goals,

        "accounts": accounts,

        "investments": investments,

        "total_account_balance":
            total_account_balance,

        "total_investment_value":
            total_investment_value,

        "account_to_investment_ratio":
            account_to_investment_ratio
    }


def get_market_data(
    ticker,
    days=30
):
    """
    Retrieves recent market data for a stock ticker.
    """

    days = int(days)

    market_data = (
        get_market_data_from_database(
            ticker
        )
    )

    columns = [
        "ticker",
        "market_date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume"
    ]

    data = convert_rows(
        market_data,
        columns
    )

    # Return only the requested number
    # of latest observations.
    return data[:days]


# ============================================================
# MACHINE LEARNING TOOL
# ============================================================

def predict_savings_risk(customer_id):
    """
    Uses the trained machine learning model
    to predict whether a customer is likely
    to reach each of their savings goals.
    """

    customer_id = validate_customer_id(
        customer_id
    )

    model_file = (
        "ai/savings_model.pkl"
    )

    model = joblib.load(
        model_file
    )

    customer = get_customer_from_database(
        customer_id
    )

    if customer is None:

        return {
            "error": (
                f"Customer {customer_id} "
                "was not found."
            )
        }

    savings_goals = (
        get_savings_goal_from_database(
            customer_id
        )
    )

    if not savings_goals:

        return {
            "error": (
                "Customer does not have "
                "a savings goal."
            )
        }

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

    income = float(
        customer["income"]
    )

    today = (
        pd.Timestamp.today()
        .normalize()
    )

    predictions = []

    for goal in savings_goals:

        goal_id = goal[0]
        goal_name = goal[2]

        target_amount = float(
            goal[3]
        )

        current_amount = float(
            goal[4]
        )

        target_date = pd.to_datetime(
            goal[5]
        )

        days_to_target = (
            target_date - today
        ).days

        savings_progress = (
            current_amount
            / target_amount
        )

        savings_progress = max(
            0,
            min(
                savings_progress,
                1
            )
        )

        remaining_amount = (
            target_amount
            - current_amount
        )

        remaining_amount = max(
            remaining_amount,
            0
        )

        months_remaining = max(
            days_to_target / 30.44,
            1
        )

        required_monthly_saving = (
            remaining_amount
            / months_remaining
        )

        required_saving_income_ratio = (
            required_monthly_saving
            / income
        )

        X_customer = pd.DataFrame([
            {
                "age": int(
                    customer["age"]
                ),

                "income": income,

                "risk_profile":
                    customer["risk_profile"],

                "customer_segment":
                    customer["customer_segment"],

                "target_amount":
                    target_amount,

                "current_amount":
                    current_amount,

                "days_to_target":
                    days_to_target,

                "savings_progress":
                    savings_progress,

                "remaining_amount":
                    remaining_amount,

                "required_monthly_saving":
                    required_monthly_saving,

                "required_saving_income_ratio":
                    required_saving_income_ratio
            }
        ])

        prediction = model.predict(
            X_customer[features]
        )[0]

        probabilities = model.predict_proba(
            X_customer[features]
        )[0]

        predictions.append({

            "goal_id":
                goal_id,

            "goal_name":
                goal_name,

            "prediction":
                (
                    "Low risk"
                    if prediction == 1
                    else "High risk"
                ),

            "probability_reach_goal":
                float(
                    probabilities[1]
                ),

            "probability_not_reach_goal":
                float(
                    probabilities[0]
                ),

            "savings_progress":
                savings_progress,

            "remaining_amount":
                remaining_amount,

            "required_monthly_saving":
                required_monthly_saving,

            "days_to_target":
                days_to_target
        })

    return {

        "customer_id":
            customer_id,

        "number_of_savings_goals":
            len(predictions),

        "savings_goals":
            predictions
    }

# ============================================================
# AI ANALYSIS - HIGH RISK SAVINGS GOALS
# ============================================================

def get_high_risk_customers():
    """
    Analyzes all savings goals using the trained
    machine learning model and identifies
    high-risk cases.
    """

    # Load the trained model
    model_file = "ai/savings_model.pkl"
    model = joblib.load(model_file)

    # Load the ML dataset
    data_file = "data/generated/savings_ml_dataset.csv"
    df = pd.read_csv(data_file)

    # Features used by the trained model
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

    # Predict all savings goals
    predictions = model.predict(
        df[features]
    )

    probabilities = model.predict_proba(
        df[features]
    )

    # Add predictions to the dataset
    df["prediction"] = predictions

    df["probability_reach_goal"] = probabilities[:, 1]

    df["probability_not_reach_goal"] = probabilities[:, 0]

    # Keep high-risk cases
    high_risk = df[
        df["prediction"] == 0
    ].copy()

    # Sort by highest risk
    high_risk = high_risk.sort_values(
        "probability_not_reach_goal",
        ascending=False
    )

    # Keep the 20 highest-risk cases
    result = high_risk[
        [
            "customer_id",
            "customer_segment",
            "risk_profile",
            "income",
            "target_amount",
            "current_amount",
            "savings_progress",
            "remaining_amount",
            "days_to_target",
            "required_monthly_saving",
            "probability_not_reach_goal"
        ]
    ].head(20)

    # Convert results into a format the LLM can use
    high_risk_customers = []

    for _, row in result.iterrows():

        high_risk_customers.append({
            "customer_id": int(
                row["customer_id"]
            ),

            "customer_segment":
                row["customer_segment"],

            "risk_profile":
                row["risk_profile"],

            "income":
                float(row["income"]),

            "target_amount":
                float(row["target_amount"]),

            "current_amount":
                float(row["current_amount"]),

            "savings_progress":
                float(row["savings_progress"]),

            "remaining_amount":
                float(row["remaining_amount"]),

            "days_to_target":
                int(row["days_to_target"]),

            "required_monthly_saving":
                float(
                    row["required_monthly_saving"]
                ),

            "probability_not_reach_goal":
                float(
                    row["probability_not_reach_goal"]
                )
        })

    return {
        "total_savings_goals_analyzed":
            int(len(df)),

        "high_risk_count":
            int(len(high_risk)),

        "high_risk_percentage":
            float(
                len(high_risk) / len(df)
            ),

        "high_risk_customers":
            high_risk_customers
    }

# ============================================================
# AI ANALYSIS - INVESTMENT RISK PROFILES
# ============================================================

def get_investment_risk_profile_analysis():
    """
    Analyzes how investments differ between
    customers with different risk profiles.
    """

    customers = get_all_customers_from_database()

    investments = get_all_investments_from_database()

    # --------------------------------------------------------
    # Create a lookup dictionary for customer risk profiles
    # --------------------------------------------------------

    customer_risk_profiles = {
        int(customer[0]): customer[3]
        for customer in customers
    }

    # --------------------------------------------------------
    # Create analysis structure
    # --------------------------------------------------------

    analysis = {
        "Low": {
            "customer_count": 0,
            "customers_with_investments": 0,
            "investment_count": 0,
            "total_investment_value": 0.0,
            "asset_types": {},
            "sectors": {}
        },

        "Medium": {
            "customer_count": 0,
            "customers_with_investments": 0,
            "investment_count": 0,
            "total_investment_value": 0.0,
            "asset_types": {},
            "sectors": {}
        },

        "High": {
            "customer_count": 0,
            "customers_with_investments": 0,
            "investment_count": 0,
            "total_investment_value": 0.0,
            "asset_types": {},
            "sectors": {}
        }
    }

    # --------------------------------------------------------
    # Count customers by risk profile
    # --------------------------------------------------------

    for customer in customers:

        risk_profile = customer[3]

        if risk_profile not in analysis:
            continue

        analysis[risk_profile][
            "customer_count"
        ] += 1

    # --------------------------------------------------------
    # Analyze investments
    # --------------------------------------------------------

    customers_with_investments = {
        "Low": set(),
        "Medium": set(),
        "High": set()
    }

    for investment in investments:

        customer_id = int(investment[1])

        asset_type = investment[3]

        sector = investment[4]

        quantity = float(investment[5])

        purchase_price = float(investment[6])

        investment_value = (
            quantity * purchase_price
        )

        # ----------------------------------------------------
        # Find the customer's risk profile
        # ----------------------------------------------------

        risk_profile = customer_risk_profiles.get(
            customer_id
        )

        if risk_profile not in analysis:
            continue

        # ----------------------------------------------------
        # Count customers with investments
        # ----------------------------------------------------

        customers_with_investments[
            risk_profile
        ].add(customer_id)

        # ----------------------------------------------------
        # Count investments
        # ----------------------------------------------------

        analysis[risk_profile][
            "investment_count"
        ] += 1

        # ----------------------------------------------------
        # Add total investment value
        # ----------------------------------------------------

        analysis[risk_profile][
            "total_investment_value"
        ] += investment_value

        # ----------------------------------------------------
        # Investment value by asset type
        # ----------------------------------------------------

        if asset_type not in analysis[
            risk_profile
        ]["asset_types"]:

            analysis[
                risk_profile
            ]["asset_types"][asset_type] = 0.0

        analysis[
            risk_profile
        ]["asset_types"][asset_type] += (
            investment_value
        )

        # ----------------------------------------------------
        # Investment value by sector
        # ----------------------------------------------------

        if sector not in analysis[
            risk_profile
        ]["sectors"]:

            analysis[
                risk_profile
            ]["sectors"][sector] = 0.0

        analysis[
            risk_profile
        ]["sectors"][sector] += (
            investment_value
        )

    # --------------------------------------------------------
    # Add number of customers with investments
    # --------------------------------------------------------

    for risk_profile in analysis:

        analysis[risk_profile][
            "customers_with_investments"
        ] = len(
            customers_with_investments[
                risk_profile
            ]
        )

    # --------------------------------------------------------
    # Calculate average investment value
    # per customer
    # --------------------------------------------------------

    for risk_profile in analysis:

        customer_count = analysis[
            risk_profile
        ]["customer_count"]

        total_value = analysis[
            risk_profile
        ]["total_investment_value"]

        average_value = (
            total_value / customer_count
            if customer_count > 0
            else 0
        )

        analysis[
            risk_profile
        ][
            "average_investment_value_per_customer"
        ] = average_value

    # --------------------------------------------------------
    # Add explicit metric descriptions
    # --------------------------------------------------------

    for risk_profile in analysis:

        analysis[risk_profile][
            "metric_definitions"
        ] = {
            "total_investment_value":
                "Total investment value across all investments belonging to customers with this risk profile.",

            "average_investment_value_per_customer":
                "Total investment value divided by the total number of customers with this risk profile.",

            "customers_with_investments":
                "Number of customers with this risk profile who have at least one investment."
        }

    return analysis

# ============================================================
# AI ANALYSIS - INVESTMENT CUSTOMER SEGMENTS
# ============================================================


def get_investment_customer_segment_analysis():
    """
    Analyzes how investments differ between
    different customer segments.
    """

    customers = get_all_customers_from_database()

    investments = get_all_investments_from_database()


    # --------------------------------------------------------
    # Create a lookup dictionary for customer segments
    # --------------------------------------------------------

    customer_segments = {
        int(customer[0]): customer[4]
        for customer in customers
    }


    # --------------------------------------------------------
    # Create analysis structure
    # --------------------------------------------------------

    analysis = {}


    # --------------------------------------------------------
    # Count customers by customer segment
    # --------------------------------------------------------

    for customer in customers:

        customer_segment = customer[4]

        if customer_segment not in analysis:

            analysis[customer_segment] = {
                "customer_count": 0,
                "customers_with_investments": 0,
                "investment_count": 0,
                "total_investment_value": 0.0,
                "asset_types": {},
                "sectors": {}
            }


        analysis[customer_segment][
            "customer_count"
        ] += 1


    # --------------------------------------------------------
    # Analyze investments
    # --------------------------------------------------------

    customers_with_investments = {
        customer_segment: set()
        for customer_segment in analysis
    }


    for investment in investments:

        customer_id = int(investment[1])

        asset_type = investment[3]

        sector = investment[4]

        quantity = float(investment[5])

        purchase_price = float(investment[6])

        investment_value = (
            quantity * purchase_price
        )


        # ----------------------------------------------------
        # Find the customer's segment
        # ----------------------------------------------------

        customer_segment = customer_segments.get(
            customer_id
        )


        if customer_segment not in analysis:
            continue


        # ----------------------------------------------------
        # Count customers with investments
        # ----------------------------------------------------

        customers_with_investments[
            customer_segment
        ].add(customer_id)


        # ----------------------------------------------------
        # Count investments
        # ----------------------------------------------------

        analysis[customer_segment][
            "investment_count"
        ] += 1


        # ----------------------------------------------------
        # Add total investment value
        # ----------------------------------------------------

        analysis[customer_segment][
            "total_investment_value"
        ] += investment_value


        # ----------------------------------------------------
        # Investment value by asset type
        # ----------------------------------------------------

        if asset_type not in analysis[
            customer_segment
        ]["asset_types"]:

            analysis[
                customer_segment
            ]["asset_types"][asset_type] = 0.0


        analysis[
            customer_segment
        ]["asset_types"][asset_type] += (
            investment_value
        )


        # ----------------------------------------------------
        # Investment value by sector
        # ----------------------------------------------------

        if sector not in analysis[
            customer_segment
        ]["sectors"]:

            analysis[
                customer_segment
            ]["sectors"][sector] = 0.0


        analysis[
            customer_segment
        ]["sectors"][sector] += (
            investment_value
        )


    # --------------------------------------------------------
    # Add number of customers with investments
    # --------------------------------------------------------

    for customer_segment in analysis:

        analysis[customer_segment][
            "customers_with_investments"
        ] = len(
            customers_with_investments[
                customer_segment
            ]
        )


    # --------------------------------------------------------
    # Calculate average investment value
    # per customer
    # --------------------------------------------------------

    for customer_segment in analysis:

        customer_count = analysis[
            customer_segment
        ]["customer_count"]

        total_value = analysis[
            customer_segment
        ]["total_investment_value"]


        analysis[
            customer_segment
        ][
            "average_investment_value_per_customer"
        ] = (

            total_value / customer_count

            if customer_count > 0

            else 0
        )


    return analysis

# ============================================================
# AI ANALYSIS - CUSTOMER FINANCIAL BEHAVIOR
# ============================================================


def get_customer_financial_behavior_analysis():
    """
    Analyzes financial behavior between
    different customer segments.
    """

    customers = get_all_customers_from_database()
    accounts = get_all_accounts_from_database()
    transactions = get_all_transactions_from_database()
    investments = get_all_investments_from_database()
    savings_goals = get_all_savings_goals_from_database()


    # --------------------------------------------------------
    # Create lookup dictionaries
    # --------------------------------------------------------

    customer_segments = {
        int(customer[0]): customer[4]
        for customer in customers
    }

    account_customers = {
        int(account[0]): int(account[1])
        for account in accounts
    }


    # --------------------------------------------------------
    # Create analysis structure
    # --------------------------------------------------------

    analysis = {}

    for customer in customers:

        customer_segment = customer[4]

        if customer_segment not in analysis:

            analysis[customer_segment] = {

                "customer_count": 0,

                "total_income": 0.0,

                "total_account_balance": 0.0,

                "account_count": 0,

                "transaction_count": 0,

                "total_transaction_amount": 0.0,

                "investment_count": 0,

                "total_investment_value": 0.0,

                "savings_goal_count": 0,

                "total_savings_target": 0.0,

                "total_current_savings": 0.0
            }


        analysis[customer_segment][
            "customer_count"
        ] += 1


        if customer[2] is not None:

            analysis[customer_segment][
                "total_income"
            ] += float(customer[2])


    # --------------------------------------------------------
    # Analyze accounts
    # --------------------------------------------------------

    for account in accounts:

        customer_id = int(account[1])

        customer_segment = customer_segments.get(
            customer_id
        )

        if customer_segment not in analysis:
            continue


        if account[3] is not None:

            balance = float(account[3])

            analysis[customer_segment][
                "total_account_balance"
            ] += balance


        analysis[customer_segment][
            "account_count"
        ] += 1


    # --------------------------------------------------------
    # Analyze transactions
    # --------------------------------------------------------

    for transaction in transactions:

        account_id = int(transaction[1])

        customer_id = account_customers.get(
            account_id
        )

        if customer_id is None:
            continue


        customer_segment = customer_segments.get(
            customer_id
        )

        if customer_segment not in analysis:
            continue


        amount = float(transaction[4])


        analysis[customer_segment][
            "transaction_count"
        ] += 1


        analysis[customer_segment][
            "total_transaction_amount"
        ] += amount


    # --------------------------------------------------------
    # Analyze investments
    # --------------------------------------------------------

    for investment in investments:

        customer_id = int(investment[1])

        customer_segment = customer_segments.get(
            customer_id
        )

        if customer_segment not in analysis:
            continue


        quantity = float(investment[5])

        purchase_price = float(investment[6])


        investment_value = (
            quantity * purchase_price
        )


        analysis[customer_segment][
            "investment_count"
        ] += 1


        analysis[customer_segment][
            "total_investment_value"
        ] += investment_value


    # --------------------------------------------------------
    # Analyze savings goals
    # --------------------------------------------------------

    for savings_goal in savings_goals:

        customer_id = int(savings_goal[1])

        customer_segment = customer_segments.get(
            customer_id
        )

        if customer_segment not in analysis:
            continue


        target_amount = float(
            savings_goal[3]
        )

        current_amount = float(
            savings_goal[4]
        )


        analysis[customer_segment][
            "savings_goal_count"
        ] += 1


        analysis[customer_segment][
            "total_savings_target"
        ] += target_amount


        analysis[customer_segment][
            "total_current_savings"
        ] += current_amount


    # --------------------------------------------------------
    # Calculate exact averages and progress
    # --------------------------------------------------------

    for customer_segment in analysis:

        customer_count = analysis[
            customer_segment
        ]["customer_count"]


        if customer_count > 0:

            analysis[customer_segment][
                "average_income"
            ] = (

                analysis[customer_segment][
                    "total_income"
                ]
                / customer_count
            )


            analysis[customer_segment][
                "average_account_balance"
            ] = (

                analysis[customer_segment][
                    "total_account_balance"
                ]
                / customer_count
            )


            analysis[customer_segment][
                "average_investment_value"
            ] = (

                analysis[customer_segment][
                    "total_investment_value"
                ]
                / customer_count
            )


        else:

            analysis[customer_segment][
                "average_income"
            ] = 0.0


            analysis[customer_segment][
                "average_account_balance"
            ] = 0.0


            analysis[customer_segment][
                "average_investment_value"
            ] = 0.0


        # ----------------------------------------------------
        # Calculate savings progress
        # ----------------------------------------------------

        savings_target = analysis[
            customer_segment
        ]["total_savings_target"]


        current_savings = analysis[
            customer_segment
        ]["total_current_savings"]


        if savings_target > 0:

            analysis[customer_segment][
                "savings_progress"
            ] = (

                current_savings
                / savings_target
            )

        else:

            analysis[customer_segment][
                "savings_progress"
            ] = 0.0


    # --------------------------------------------------------
    # Calculate exact segment comparisons
    # --------------------------------------------------------

    highest_average_income = max(
        analysis.items(),
        key=lambda item:
        item[1]["average_income"]
    )


    highest_average_balance = max(
        analysis.items(),
        key=lambda item:
        item[1]["average_account_balance"]
    )


    highest_average_investment = max(
        analysis.items(),
        key=lambda item:
        item[1]["average_investment_value"]
    )


    highest_savings_progress = max(
        analysis.items(),
        key=lambda item:
        item[1]["savings_progress"]
    )


    # --------------------------------------------------------
    # Return analysis
    # --------------------------------------------------------

    return {

        "segment_analysis": analysis,

        "highest_average_income": {
            "customer_segment":
                highest_average_income[0],

            "value":
                highest_average_income[1][
                    "average_income"
                ]
        },

        "highest_average_account_balance": {
            "customer_segment":
                highest_average_balance[0],

            "value":
                highest_average_balance[1][
                    "average_account_balance"
                ]
        },

        "highest_average_investment_value": {
            "customer_segment":
                highest_average_investment[0],

            "value":
                highest_average_investment[1][
                    "average_investment_value"
                ]
        },

        "highest_savings_progress": {
            "customer_segment":
                highest_savings_progress[0],

            "value":
                highest_savings_progress[1][
                    "savings_progress"
                ]
        }
    }

# ============================================================
# AI ANALYSIS - KEY CUSTOMER INSIGHTS
# ============================================================


def get_key_customer_insights():
    """
    Combines the existing customer analyses
    and returns the most important calculated
    results for the LLM to explain.
    """

    # --------------------------------------------------------
    # Get results from existing analysis tools
    # --------------------------------------------------------

    savings_risk = get_high_risk_customers()

    investment_risk_profiles = (
        get_investment_risk_profile_analysis()
    )

    investment_segments = (
        get_investment_customer_segment_analysis()
    )

    financial_behavior = (
        get_customer_financial_behavior_analysis()
    )


    # --------------------------------------------------------
    # Find highest average investment value
    # by risk profile
    # --------------------------------------------------------

    highest_average_investment_risk = max(
        investment_risk_profiles,
        key=lambda risk_profile:
            investment_risk_profiles[
                risk_profile
            ][
                "average_investment_value_per_customer"
            ]
    )

    highest_average_investment_value = (
        investment_risk_profiles[
            highest_average_investment_risk
        ][
            "average_investment_value_per_customer"
        ]
    )


    # --------------------------------------------------------
    # Find highest total investment value
    # by customer segment
    # --------------------------------------------------------

    highest_investment_segment = max(
        investment_segments,
        key=lambda segment:
            investment_segments[
                segment
            ][
                "total_investment_value"
            ]
    )

    highest_total_investment_value = (
        investment_segments[
            highest_investment_segment
        ][
            "total_investment_value"
        ]
    )


    # --------------------------------------------------------
    # Get already calculated financial behavior results
    # --------------------------------------------------------

    highest_income = (
        financial_behavior[
            "highest_average_income"
        ]
    )

    highest_balance = (
        financial_behavior[
            "highest_average_account_balance"
        ]
    )

    highest_investment = (
        financial_behavior[
            "highest_average_investment_value"
        ]
    )

    highest_savings_progress = (
        financial_behavior[
            "highest_savings_progress"
        ]
    )


    # --------------------------------------------------------
    # Calculate high-risk savings goal percentage
    # --------------------------------------------------------

    total_savings_goals = (
        savings_risk[
            "total_savings_goals_analyzed"
        ]
    )

    high_risk_count = (
        savings_risk[
            "high_risk_count"
        ]
    )

    high_risk_percentage = (
        high_risk_count
        / total_savings_goals
        * 100
        if total_savings_goals > 0
        else 0
    )


    # --------------------------------------------------------
    # Return exact calculated results
    # --------------------------------------------------------

    return {

        "savings_risk": {

            "total_savings_goals_analyzed":
                total_savings_goals,

            "high_risk_count":
                high_risk_count,

            "high_risk_percentage":
                high_risk_percentage
        },


        "investment_by_risk_profile": {

            "highest_average_investment_risk_profile":
                highest_average_investment_risk,

            "highest_average_investment_value":
                highest_average_investment_value
        },


        "investment_by_customer_segment": {

            "highest_total_investment_segment":
                highest_investment_segment,

            "highest_total_investment_value":
                highest_total_investment_value
        },


        "financial_behavior": {

            "highest_average_income_segment":
                highest_income[
                    "customer_segment"
                ],

            "highest_average_income":
                highest_income[
                    "value"
                ],

            "highest_average_account_balance_segment":
                highest_balance[
                    "customer_segment"
                ],

            "highest_average_account_balance":
                highest_balance[
                    "value"
                ],

            "highest_average_investment_value_segment":
                highest_investment[
                    "customer_segment"
                ],

            "highest_average_investment_value":
                highest_investment[
                    "value"
                ],

            "highest_savings_progress_segment":
                highest_savings_progress[
                    "customer_segment"
                ],

            "highest_savings_progress":
                highest_savings_progress[
                    "value"
                ]
        }
    }

# ============================================================
# TOOLS AVAILABLE TO THE LLM
# ============================================================

tools = [

    {
        "type": "function",
        "function": {
            "name": "get_customer",

            "description": (
                "Get basic information about a bank "
                "customer. Use this for questions about "
                "age, income, risk profile or customer "
                "segment."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description":
                            "The customer ID."
                    }
                },

                "required": [
                    "customer_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_savings_goals",

            "description": (
                "Get the raw savings goals for a customer, "
                "including goal names, target amounts, current "
                "amounts and target dates. Use this only when "
                "the user asks for savings goal information "
                "without asking for risk predictions or the "
                "probability of reaching the goals."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description":
                            "The customer ID."
                    }
                },

                "required": [
                    "customer_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_accounts",

            "description": (
                "Get all bank accounts belonging "
                "to a customer."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description":
                            "The customer ID."
                    }
                },

                "required": [
                    "customer_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_transactions",

            "description": (
                "Retrieve and list the transaction records for "
                "one specific customer. Use this tool when the "
                "user asks what transactions a customer has. "
                "Return the transactions directly using the "
                "transaction date, amount, category and "
                "transaction type provided by the tool. "
                "Do not summarize, analyze, group, count or "
                "calculate totals unless the user explicitly "
                "asks for an analysis or calculation."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description":
                            "The customer ID."
                    }
                },

                "required": [
                    "customer_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_investments",

            "description": (
                "Get investments owned by a customer, "
                "including ticker, sector, quantity "
                "and purchase price."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description":
                            "The customer ID."
                    }
                },

                "required": [
                    "customer_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name":
                "get_customer_financial_overview",

            "description": (
                "Get a combined financial overview "
                "of a customer. This tool retrieves "
                "customer information, savings goals, "
                "bank accounts and investments. "
                "Use this tool when a question requires "
                "multiple types of financial information "
                "for the same customer, especially when "
                "the user asks to compare account balances "
                "with investment value or asks for a "
                "financial overview."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description":
                            "The customer ID."
                    }
                },

                "required": [
                    "customer_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_market_data",

            "description": (
                "Get recent market data for a stock "
                "ticker. Use this for questions about "
                "stock prices or recent market data."
            ),

            "parameters": {
                "type": "object",

                "properties": {

                    "ticker": {
                        "type": "string",
                        "description":
                            "Stock ticker, for example SEB-A."
                    },

                    "days": {
                        "type": "integer",
                        "description":
                            "Number of latest observations "
                            "to retrieve."
                    }
                },

                "required": [
                    "ticker"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name":
                "predict_savings_risk",

            "description": (
                "Predict the probability of reaching each "
                "savings goal for one specific customer. "
                "Use this tool only when a specific customer "
                "ID is provided. It analyzes all savings goals "
                "belonging to that customer and returns a risk "
                "prediction and probability for each goal."
            ),

            "parameters": {
                "type": "object",

                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description":
                            "The customer ID."
                    }
                },

                "required": [
                    "customer_id"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_high_risk_customers",

            "description": (
                "Analyze savings goals across all customers "
                "using the machine learning model. Use this "
                "tool when the user asks which customers or "
                "which savings goals have the highest risk "
                "of not being reached across multiple "
                "customers. Do not use this tool for a "
                "specific customer."
            ),


            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name":
                "get_investment_risk_profile_analysis",

            "description": (
                "Analyze how investments differ between "
                "customers with different risk profiles. "
                "The analysis includes customer counts, "
                "number of investments, total investment "
                "value, average investment value per "
                "customer, investment value by asset type "
                "and investment value by sector."
            ),

            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_investment_customer_segment_analysis",
            "description": (
                "Analyze how investments differ between "
                "different customer segments. Use this "
                "for questions about investment values, "
                "investment counts, asset types or sectors "
                "across customer segments."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_customer_financial_behavior_analysis",
            "description": (
                "Analyze financial behavior across "
                "different customer segments using "
                "income, account balances, transactions, "
                "investments and savings goals."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_key_customer_insights",
            "description": (
                "Analyze the overall Nordic Bank customer data "
                "and identify the most important findings and "
                "what they mean for the bank."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# ============================================================
# TOOL DISPATCHER
# ============================================================

def execute_tool(
    tool_name,
    arguments
):
    """
    Executes the function selected by the LLM.
    """

    if tool_name == "get_customer":

        return get_customer(
            arguments["customer_id"]
        )

    if tool_name == "get_savings_goals":

        return get_savings_goals(
            arguments["customer_id"]
        )

    if tool_name == "get_accounts":

        return get_accounts(
            arguments["customer_id"]
        )

    if tool_name == "get_transactions":

        return get_transactions(
            arguments["customer_id"]
        )

    if tool_name == "get_investments":

        return get_investments(
            arguments["customer_id"]
        )

    if (
        tool_name
        == "get_customer_financial_overview"
    ):

        return get_customer_financial_overview(
            arguments["customer_id"]
        )

    if tool_name == "get_market_data":

        return get_market_data(
            arguments["ticker"],
            arguments.get(
                "days",
                30
            )
        )

    if (
        tool_name
        == "predict_savings_risk"
    ):

        return predict_savings_risk(
            arguments["customer_id"]
        )

    if (
        tool_name
        == "get_high_risk_customers"
    ):

        return get_high_risk_customers()

    if (
        tool_name
        == "get_investment_risk_profile_analysis"
    ):

        return get_investment_risk_profile_analysis()

    if (
        tool_name
        == "get_investment_customer_segment_analysis"
    ):
        return get_investment_customer_segment_analysis()

    if (
        tool_name
        == "get_customer_financial_behavior_analysis"
    ):
        return get_customer_financial_behavior_analysis()

    if (
        tool_name
        == "get_key_customer_insights"
    ):
        return get_key_customer_insights()

    return {
        "error":
            f"Unknown tool: {tool_name}"
    }


# ============================================================
# SYSTEM INSTRUCTIONS
# ============================================================

SYSTEM_PROMPT = """
You are the AI assistant for a fictional bank
called Nordic Bank.

You help analyze customer, account,
transaction, investment, savings and
market data.

Important rules:

1. Use the available tools whenever the user asks
   about actual Nordic Bank data.

2. Never invent information. Only report information
   returned by the available tools. If the requested
   information is not available, say so.

3. Use get_customer_financial_overview when the user
   asks for a financial overview or when the question
   requires multiple types of financial information
   for the same customer.

4. Use the specific database tool when the question
   concerns only one type of data.

5. When using get_transactions, answer the user's
   question directly using the returned transaction
   records. If the user asks what transactions a
   customer has, simply list the transactions. Do not
   perform calculations, create summaries, write code,
   or answer a different question unless explicitly
   asked.

6. Use predict_savings_risk when the user asks about
   savings goal risk, the likelihood or probability
   of reaching a savings goal, or asks to analyze the
   savings goals of a specific customer.

7. When using predict_savings_risk, report all savings
   goals returned by the tool. For each goal, report
   its goal name, risk prediction and probability of
   reaching the goal when available.

8. Do not invent goal names, financial products,
   recommendations, explanations or other information
   that is not present in the tool result.

9. Use get_high_risk_customers when the user asks
   which customers or savings goals have a high risk
   of not being reached across multiple customers.
   Distinguish between customers and savings goals.

10. Use get_investment_risk_profile_analysis when the
    user asks how investments differ between customers
    with different risk profiles.

11. Use get_investment_customer_segment_analysis when
    the user asks how investments differ between
    customer segments.

12. Use get_customer_financial_behavior_analysis when
    the user asks about financial behavior, income,
    account balances, transactions, investments or
    savings across customer segments.

13. Use get_key_customer_insights when the user asks
    for the most important insights, key findings,
    an overall analysis of the customer data, or what
    the findings mean for Nordic Bank.

14. When reporting results from analysis tools, only
    describe values, patterns and relationships directly
    supported by the returned data. Do not invent causes,
    explanations or assumptions.

15. Do not invent percentages, volatility, performance,
    returns, stability, diversification or other metrics
    that are not provided by the tools. Do not calculate
    additional metrics unless the user explicitly asks.

16. Clearly distinguish between total and average values.
    When comparing metrics, always associate the correct
    category or segment with the correct metric.

17. When discussing sectors, asset types, customer
    segments or risk profiles, use the values returned
    by the relevant tool. Do not translate or modify
    categorical values.

18. Do not infer investment strategies, preferences,
    diversification, allocation, trends or causes from
    investment data unless directly supported by the tool.

19. Do not mention internal technical field names such
    as probability_not_reach_goal or goal_id unless the
    user specifically asks about the technical
    implementation.

20. All monetary values are in SEK.

21. The data is synthetic and belongs to a fictional
    bank called Nordic Bank.

22. The savings prediction model is a proof-of-concept
    trained on synthetic data. Do not present it as a
    validated banking risk model.

23. Answer in English. Keep answers concise, clear
    and easy to understand.

24. When you need to use a tool, call the tool directly.
    Do not write the tool name or tool parameters as
    ordinary text or JSON in the answer.

25. If the requested information is not available in
    the database or available tools, do not call an
    unrelated tool. State that the information is not
    available.

26. If a tool call is required, execute the tool and use
    its result to answer the user's question. Do not
    output a JSON tool call as the final answer.
"""

# ============================================================
# MAIN AI ASSISTANT
# ============================================================


def ask_ai(question):
    """
    Sends a question to the local LLM and
    allows the model to call database and
    machine learning tools.
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # ----------------------------------------------------
    # Check whether the question asks for unavailable data
    # ----------------------------------------------------

    unavailable_topics = [
        "credit score",
        "credit scores"
    ]

    question_lower = question.lower()

    if any(
        topic in question_lower
        for topic in unavailable_topics
    ):
        return (
            "Credit score data is not available "
            "in the Nordic Bank database or "
            "available tools."
        )

    while True:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            tools=tools
        )

        messages.append(
            response.message
        )

        # ----------------------------------------------------
        # Normal tool calling
        # ----------------------------------------------------

        if response.message.tool_calls:

            for tool_call in response.message.tool_calls:

                tool_name = (
                    tool_call.function.name
                )

                arguments = (
                    tool_call.function.arguments
                )

                print(
                    f"\n[AI is using tool: "
                    f"{tool_name}]"
                )

                try:
                    result = execute_tool(
                        tool_name,
                        arguments
                    )
                except Exception as error:
                    result = {
                        "error": str(error)
                    }

                messages.append({
                    "role": "tool",
                    "content": json.dumps(
                        result,
                        ensure_ascii=False
                    )
                })

            continue

        # ----------------------------------------------------
        # Fallback if the model writes a tool call as JSON
        # ----------------------------------------------------

        content = response.message.content

        if content:

            try:
                possible_tool_call = json.loads(content)

                if (
                    isinstance(possible_tool_call, dict)
                    and "name" in possible_tool_call
                ):

                    tool_name = possible_tool_call["name"]

                    arguments = possible_tool_call.get(
                        "parameters",
                        {}
                    )

                    valid_tool_names = {
                        tool["function"]["name"]
                        for tool in tools
                    }

                    if tool_name in valid_tool_names:

                        print(
                            f"\n[AI is using tool: "
                            f"{tool_name}]"
                        )

                        try:
                            result = execute_tool(
                                tool_name,
                                arguments
                            )
                        except Exception as error:
                            result = {
                                "error": str(error)
                            }

                        messages.append({
                            "role": "tool",
                            "content": json.dumps(
                                result,
                                ensure_ascii=False
                            )
                        })

                        continue

            except (
                json.JSONDecodeError,
                TypeError
            ):
                pass

        # ----------------------------------------------------
        # No tool was requested
        # ----------------------------------------------------

        return content

# ============================================================
# CHAT LOOP
# ============================================================

print()

print(
    "=========================================="
)

print(
    "NORDIC BANK - LOCAL AI ASSISTANT"
)

print(
    "=========================================="
)

print()

print(
    "Powered by Llama 3.2 running locally."
)

print(
    "Type 'exit' to close the assistant."
)

print()


while True:

    question = input(
        "You: "
    )

    if question.lower() == "exit":

        print()

        print(
            "AI Assistant closed."
        )

        break

    if not question.strip():

        continue

    try:

        answer = ask_ai(
            question
        )

        print()

        print(
            "AI:"
        )

        print(
            answer
        )

        print()

    except Exception as error:

        print()

        print(
            "An error occurred:"
        )

        print(
            error
        )

        print()