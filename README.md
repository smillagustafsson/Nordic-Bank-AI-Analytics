# Nordic Bank – AI & Investment Analytics

## Overview

Nordic Bank – AI & Investment Analytics is a fictional banking analytics project that combines data engineering, business intelligence, machine learning and generative AI.

The project demonstrates how customer, account, transaction, investment, savings and market data can be stored, analyzed and used by an AI-powered financial assistant.

All banking data is synthetically generated and belongs to the fictional Nordic Bank.

## Project Objectives

The project was developed to demonstrate:

- Relational database design using PostgreSQL
- Data generation and ETL using Python
- SQL-based data analysis
- Business intelligence and visualization using Power BI
- Machine learning for savings goal risk prediction
- Generative AI with tool calling
- Integration between an LLM, databases and machine learning models

## Architecture

```text
Synthetic Banking Data
        ↓
      Python
        ↓
   PostgreSQL
        ↓
   SQL Analysis
        ↓
 ┌───────────────┬────────────────┐
 ↓               ↓                ↓
Power BI      Machine Learning   AI Assistant
                                  ↓
                               Ollama
                                  ↓
                              Llama 3.2
                                  ↓
                         Database / ML Tools

```

## Database
The PostgreSQL database contains the following main entities:
- Customers
- Accounts
- Transactions
- Investments
- Savings Goals
- Market Data
The database uses primary keys and foreign keys to represent relationships between customers, accounts, transactions, investments and savings goals.

## Data Generation and ETL
Python scripts are used to generate and prepare synthetic banking data.
The project includes scripts for:
- Generating customers
- Generating accounts
- Generating transactions
- Generating investments
- Generating savings goals
- Fetching historical market data
- Preparing machine learning data
- Loading data into PostgreSQL
The generated data is designed to simulate a realistic banking environment while remaining completely synthetic.

## SQL Analysis
SQL queries are used to analyze the banking data, including:
- Customer segments and risk profiles
- Account balances
- Transaction activity
- Investment holdings
- Savings goals
- Market data
- Investment performance

The SQL analysis is stored in:
database/analysis.sql

The database structure is defined in:
database/schema.sql

## Machine Learning
A machine learning model is used to estimate the probability that a customer will reach their savings goal.

The model uses features such as:
- Income
- Age
- Target amount
- Current savings
- Savings progress
- Remaining amount
- Required monthly saving
- Days to target
- Customer segment
- Risk profile
A logistic regression model is trained using synthetic data.

The trained model is stored in:
ai/savings_model.pkl

The model is a proof-of-concept trained on synthetic data and should not be interpreted as a validated banking risk model.

## AI Assistant
The project includes a local AI financial assistant powered by:
- Ollama
- Llama 3.2
- Python
- PostgreSQL
- Machine learning tools
The assistant uses tool calling to retrieve and analyze information from the database and machine learning model.

For example, the assistant can answer questions such as:
- What is the income of customer 50?
- What transactions does customer 50 have?
- What investments does customer 50 have?
- Analyze all savings goals for customer 80.
- Which savings goals have the highest risk of not being reached?
- What is the total and average investment value for each risk profile?
- Which customer segment has the highest total investment value?
- What are the key insights from the Nordic Bank customer data?
The assistant selects the appropriate tool based on the user's question and returns the result in natural language.

The AI assistant is implemented in:
ai/llm_assistant.py

## Power BI Dashboard
A Power BI dashboard was developed to visualize the Nordic Bank data.
The dashboard includes:
- Number of customers
- Total account balance
- Stock price development over time
- Investment value by sector
- Customers by customer segment
- Savings progress
- Transactions by category
- Customer risk profile distribution
- Account balance by customer segment

The Power BI report is available in:
powerbi/Rapport Nordic Bank.pbix

A preview of the dashboard is also included:
powerbi/Bank_dashboard.png

## Technologies
- Python
- PostgreSQL
- SQL
- Pandas
- NumPy
- Scikit-learn
- Joblib
- yfinance
- Ollama
- Llama 3.2
- Power BI
- DAX

## Project Structure
Nordic-Bank-AI-Analytics/
│
├── ai/
│   ├── database_connection.py
│   ├── llm_assistant.py
│   ├── predict_savings_risk.py
│   ├── train_savings_model.py
│   └── savings_model.pkl
│
├── data/
│   └── generated/
│       ├── customers.csv
│       └── savings_ml_dataset.csv
│
├── database/
│   ├── analysis.sql
│   └── schema.sql
│
├── powerbi/
│   ├── Bank_dashboard.png
│   └── Rapport Nordic Bank.pbix
│
├── src/
│   ├── fetch_market_data.py
│   ├── generate_accounts.py
│   ├── generate_customers.py
│   ├── generate_investments.py
│   ├── generate_savings_goals.py
│   ├── generate_transactions.py
│   ├── load_customers.py
│   └── prepare_ml_data.py
│
├── .gitignore
├── README.md
└── requirements.txt

## How to Run
1. Create the PostgreSQL database
Create a PostgreSQL database called:
nordic_bank
2. Create the database schema
Run:
database/schema.sql
3. Install Python dependencies
Create and activate a virtual environment and install:
pip install -r requirements.txt

4. Generate the synthetic data
Run the relevant Python scripts in src/ to generate:
- Customers
- Accounts
- Investments
- Savings goals
- Transactions
5. Load the data into PostgreSQL
Run the data loading scripts and market data script.
6. Prepare the machine learning data
Run:
src/prepare_ml_data.py
7. Train the machine learning model
Run:
ai/train_savings_model.py
8. Run the AI assistant
Start Ollama with the required local model and run:
ai/llm_assistant.py

## Limitations
- All banking data is synthetic.
- Nordic Bank is a fictional organization.
- The savings risk model is a proof-of-concept trained on synthetic data.
- The machine learning model has not been validated using real banking data.
- The AI assistant only has access to the information provided by its available tools.