import psycopg
import getpass
import pandas as pd


# ---------------------------------------------------------
# PostgreSQL connection
# ---------------------------------------------------------

_connection = None


def get_connection():

    global _connection

    if _connection is None or _connection.closed:

        password = getpass.getpass(
            "Enter PostgreSQL password: "
        )

        _connection = psycopg.connect(
            host="localhost",
            port=5432,
            dbname="nordic_bank",
            user="postgres",
            password=password
        )

    return _connection


# ---------------------------------------------------------
# Customer
# ---------------------------------------------------------

def get_customer_from_database(customer_id):

    connection = get_connection()

    query = """
    SELECT
        customer_id,
        age,
        income,
        risk_profile,
        customer_segment
    FROM Customer
    WHERE customer_id = %s;
    """

    columns = [
        "customer_id",
        "age",
        "income",
        "risk_profile",
        "customer_segment"
    ]

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            (customer_id,)
        )

        customer = cursor.fetchone()

    if customer is None:

        return None

    return pd.Series(
        customer,
        index=columns
    )


# ---------------------------------------------------------
# All Customers
# ---------------------------------------------------------

def get_all_customers_from_database():
    """
    Retrieves all customers from the database.
    """

    connection = get_connection()

    query = """
    SELECT
        customer_id,
        age,
        income,
        risk_profile,
        customer_segment
    FROM Customer
    ORDER BY customer_id;
    """

    with connection.cursor() as cursor:

        cursor.execute(query)

        customers = cursor.fetchall()

    return customers


# ---------------------------------------------------------
# SavingsGoal
# ---------------------------------------------------------

def get_savings_goal_from_database(customer_id):

    connection = get_connection()

    query = """
    SELECT
        goal_id,
        customer_id,
        goal_name,
        target_amount,
        current_amount,
        target_date
    FROM SavingsGoal
    WHERE customer_id = %s
    ORDER BY goal_id;
    """

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            (customer_id,)
        )

        savings_goals = cursor.fetchall()

    return savings_goals


# ---------------------------------------------------------
# All SavingsGoals
# ---------------------------------------------------------

def get_all_savings_goals_from_database():
    """
    Retrieves all savings goals from the database.
    """

    connection = get_connection()

    query = """
    SELECT
        goal_id,
        customer_id,
        goal_name,
        target_amount,
        current_amount,
        target_date
    FROM SavingsGoal
    ORDER BY customer_id, goal_id;
    """

    with connection.cursor() as cursor:

        cursor.execute(query)

        savings_goals = cursor.fetchall()

    return savings_goals


# ---------------------------------------------------------
# Account
# ---------------------------------------------------------

def get_accounts_from_database(customer_id):

    connection = get_connection()

    query = """
    SELECT
        account_id,
        customer_id,
        account_type,
        balance,
        opened_date
    FROM Account
    WHERE customer_id = %s
    ORDER BY account_id;
    """

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            (customer_id,)
        )

        accounts = cursor.fetchall()

    return accounts


# ---------------------------------------------------------
# All Accounts
# ---------------------------------------------------------

def get_all_accounts_from_database():
    """
    Retrieves all accounts from the database.
    """

    connection = get_connection()

    query = """
    SELECT
        account_id,
        customer_id,
        account_type,
        balance,
        opened_date
    FROM Account
    ORDER BY customer_id, account_id;
    """

    with connection.cursor() as cursor:

        cursor.execute(query)

        accounts = cursor.fetchall()

    return accounts


# ---------------------------------------------------------
# Transactions
# ---------------------------------------------------------

def get_transactions_from_database(customer_id):

    connection = get_connection()

    query = """
    SELECT
        t.transaction_id,
        t.account_id,
        t.transaction_date,
        t.amount,
        t.category,
        t.transaction_type
    FROM Transactions t
    JOIN Account a
        ON t.account_id = a.account_id
    WHERE a.customer_id = %s
    ORDER BY t.transaction_date DESC;
    """

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            (customer_id,)
        )

        transactions = cursor.fetchall()

    return transactions


# ---------------------------------------------------------
# All Transactions
# ---------------------------------------------------------

def get_all_transactions_from_database():
    """
    Retrieves all transactions from the database.
    """

    connection = get_connection()

    query = """
    SELECT
        t.transaction_id,
        t.account_id,
        a.customer_id,
        t.transaction_date,
        t.amount,
        t.category,
        t.transaction_type
    FROM Transactions t
    JOIN Account a
        ON t.account_id = a.account_id
    ORDER BY a.customer_id, t.transaction_date DESC;
    """

    with connection.cursor() as cursor:

        cursor.execute(query)

        transactions = cursor.fetchall()

    return transactions


# ---------------------------------------------------------
# Investment
# ---------------------------------------------------------

def get_investments_from_database(customer_id):

    connection = get_connection()

    query = """
    SELECT
        investment_id,
        customer_id,
        ticker,
        asset_type,
        sector,
        quantity,
        purchase_price,
        purchase_date
    FROM Investment
    WHERE customer_id = %s
    ORDER BY purchase_date DESC;
    """

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            (customer_id,)
        )

        investments = cursor.fetchall()

    return investments


# ---------------------------------------------------------
# All Investments
# ---------------------------------------------------------

def get_all_investments_from_database():
    """
    Retrieves all investments from the database.
    """

    connection = get_connection()

    query = """
    SELECT
        investment_id,
        customer_id,
        ticker,
        asset_type,
        sector,
        quantity,
        purchase_price,
        purchase_date
    FROM Investment
    ORDER BY customer_id, investment_id;
    """

    with connection.cursor() as cursor:

        cursor.execute(query)

        investments = cursor.fetchall()

    return investments


# ---------------------------------------------------------
# MarketData
# ---------------------------------------------------------

def get_market_data_from_database(ticker):

    connection = get_connection()

    query = """
    SELECT
        ticker,
        market_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume
    FROM MarketData
    WHERE ticker = %s
    ORDER BY market_date DESC;
    """

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            (ticker,)
        )

        market_data = cursor.fetchall()

    return market_data