import getpass
from datetime import date

import psycopg
import yfinance as yf


# ---------------------------------------------------------
# DATABASE CONNECTION
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
# GET TICKERS FROM INVESTMENT TABLE
# ---------------------------------------------------------

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT DISTINCT ticker
        FROM Investment
        ORDER BY ticker
    """)

    tickers = [row[0] for row in cursor.fetchall()]


print(f"Found {len(tickers)} unique tickers.")


# ---------------------------------------------------------
# DOWNLOAD MARKET DATA
# ---------------------------------------------------------

market_data = []

for ticker in tickers:

    # Swedish stocks use .ST on Yahoo Finance
    yahoo_ticker = f"{ticker}.ST"

    print(f"Downloading data for {yahoo_ticker}...")

    try:
        stock = yf.Ticker(yahoo_ticker)

        history = stock.history(
            period="5y",
            interval="1d",
            auto_adjust=False
        )

        if history.empty:
            print(f"No data found for {yahoo_ticker}")
            continue

        for market_date, row in history.iterrows():

            if (
                row["Open"] is None
                or row["High"] is None
                or row["Low"] is None
                or row["Close"] is None
            ):
                continue

            market_data.append((
                ticker,
                market_date.date(),
                round(float(row["Open"]), 2),
                round(float(row["High"]), 2),
                round(float(row["Low"]), 2),
                round(float(row["Close"]), 2),
                int(row["Volume"])
            ))

    except Exception as error:
        print(f"Error downloading {yahoo_ticker}: {error}")


# ---------------------------------------------------------
# INSERT INTO POSTGRESQL
# ---------------------------------------------------------

with connection:
    with connection.cursor() as cursor:

        cursor.executemany(
            """
            INSERT INTO MarketData (
                ticker,
                market_date,
                open_price,
                high_price,
                low_price,
                close_price,
                volume
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, market_date) DO NOTHING
            """,
            market_data
        )


connection.close()

print()
print(f"Successfully loaded {len(market_data)} market data rows.")