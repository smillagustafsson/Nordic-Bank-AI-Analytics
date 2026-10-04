-- ============================================================
-- NORDIC BANK - AI & INVESTMENT ANALYTICS
-- SQL BUSINESS ANALYSIS
-- ============================================================

-- Purpose:
-- This file contains SQL analyses designed to answer
-- business questions related to customers, accounts,
-- transactions, investments, savings goals and market data.
--
-- Database: PostgreSQL
-- ============================================================


-- ============================================================
-- 1. CUSTOMER ANALYSIS
-- ============================================================


-- 1.1 Customers by customer segment
--
-- Business question:
-- How are customers distributed across customer segments?
--
-- Use:
-- Helps the bank understand the size of each customer segment.
-- ============================================================

SELECT
    customer_segment,
    COUNT(*) AS number_of_customers
FROM Customer
GROUP BY customer_segment
ORDER BY number_of_customers DESC;


-- 1.2 Customers by risk profile
--
-- Business question:
-- How are customers distributed across risk profiles?
--
-- Use:
-- Helps the bank understand the composition of its
-- customer base from an investment-risk perspective.
-- ============================================================

SELECT
    risk_profile,
    COUNT(*) AS number_of_customers
FROM Customer
GROUP BY risk_profile
ORDER BY number_of_customers DESC;


-- 1.3 Average income by customer segment
--
-- Business question:
-- Which customer segments have the highest average income?
--
-- Use:
-- Can support customer segmentation and financial analysis.
-- ============================================================

SELECT
    customer_segment,
    ROUND(AVG(income), 2) AS average_income
FROM Customer
GROUP BY customer_segment
ORDER BY average_income DESC;


-- ============================================================
-- 2. ACCOUNT ANALYSIS
-- ============================================================


-- 2.1 Total balance in the bank
--
-- Business question:
-- What is the total balance held across all customer accounts?
--
-- Use:
-- Provides a high-level overview of total customer balances.
-- ============================================================

SELECT
    ROUND(SUM(balance), 2) AS total_balance
FROM Account;


-- 2.2 Average account balance by customer segment
--
-- Business question:
-- How does the average account balance differ between
-- customer segments?
--
-- Use:
-- Helps identify differences in financial position across
-- customer segments.
-- ============================================================

SELECT
    c.customer_segment,
    COUNT(a.account_id) AS number_of_accounts,
    ROUND(AVG(a.balance), 2) AS average_balance
FROM Customer c
JOIN Account a
    ON c.customer_id = a.customer_id
GROUP BY c.customer_segment
ORDER BY average_balance DESC;


-- 2.3 Number of accounts by account type
--
-- Business question:
-- How many accounts exist for each account type?
--
-- Use:
-- Provides an overview of the bank's account portfolio.
-- ============================================================

SELECT
    account_type,
    COUNT(*) AS number_of_accounts
FROM Account
GROUP BY account_type
ORDER BY number_of_accounts DESC;


-- ============================================================
-- 3. TRANSACTION ANALYSIS
-- ============================================================


-- 3.1 Expenses by transaction category
--
-- Business question:
-- Which expense categories account for the largest
-- transaction amounts?
--
-- Use:
-- Helps identify major areas of customer spending.
-- ============================================================

SELECT
    category,
    COUNT(*) AS number_of_transactions,
    ROUND(SUM(amount), 2) AS total_amount
FROM Transactions
WHERE transaction_type = 'Expense'
GROUP BY category
ORDER BY total_amount DESC;


-- 3.2 Average expense by category
--
-- Business question:
-- What is the average transaction amount for each
-- expense category?
--
-- Use:
-- Helps distinguish frequent smaller expenses from
-- categories with larger individual transactions.
-- ============================================================

SELECT
    category,
    ROUND(AVG(amount), 2) AS average_expense
FROM Transactions
WHERE transaction_type = 'Expense'
GROUP BY category
ORDER BY average_expense DESC;


-- 3.3 Income versus expenses
--
-- Business question:
-- How do total income and total expenses compare?
--
-- Use:
-- Provides a high-level view of transaction flows.
-- ============================================================

SELECT
    transaction_type,
    COUNT(*) AS number_of_transactions,
    ROUND(SUM(amount), 2) AS total_amount
FROM Transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;


-- ============================================================
-- 4. INVESTMENT ANALYSIS
-- ============================================================


-- 4.1 Investment value by sector
--
-- Business question:
-- Which sectors represent the largest investment values?
--
-- Calculation:
-- Investment value = quantity × purchase price
--
-- Use:
-- Helps the bank understand how customers' investments
-- are distributed across sectors.
-- ============================================================

SELECT
    sector,
    COUNT(*) AS number_of_investments,
    ROUND(SUM(quantity * purchase_price), 2) AS invested_amount
FROM Investment
GROUP BY sector
ORDER BY invested_amount DESC;


-- 4.2 Investment value by risk profile
--
-- Business question:
-- How does investment activity differ between customer
-- risk profiles?
--
-- Use:
-- Connects customer characteristics with investment behavior.
-- ============================================================

SELECT
    c.risk_profile,
    COUNT(i.investment_id) AS number_of_investments,
    ROUND(SUM(i.quantity * i.purchase_price), 2) AS invested_amount
FROM Customer c
JOIN Investment i
    ON c.customer_id = i.customer_id
GROUP BY c.risk_profile
ORDER BY invested_amount DESC;


-- 4.3 Investment value by customer segment
--
-- Business question:
-- Which customer segments have the largest investment values?
--
-- Use:
-- Helps compare investment behavior between customer segments.
-- ============================================================

SELECT
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS number_of_customers,
    ROUND(
        SUM(i.quantity * i.purchase_price),
        2
    ) AS total_invested_amount,
    ROUND(
        AVG(i.quantity * i.purchase_price),
        2
    ) AS average_investment
FROM Customer c
JOIN Investment i
    ON c.customer_id = i.customer_id
GROUP BY c.customer_segment
ORDER BY total_invested_amount DESC;


-- ============================================================
-- 5. SAVINGS ANALYSIS
-- ============================================================


-- 5.1 Savings by goal type
--
-- Business question:
-- What are the average target and saved amounts for
-- different savings goals?
--
-- Use:
-- Helps the bank understand customers' savings priorities.
-- ============================================================

SELECT
    goal_name,
    COUNT(*) AS number_of_goals,
    ROUND(AVG(target_amount), 2) AS average_target,
    ROUND(AVG(current_amount), 2) AS average_saved
FROM SavingsGoal
GROUP BY goal_name
ORDER BY average_target DESC;


-- 5.2 Savings goal progress
--
-- Business question:
-- How close are customers to reaching their savings goals?
--
-- Calculation:
-- Progress = current amount / target amount × 100
--
-- Use:
-- Identifies which types of savings goals customers are
-- closest to completing.
-- ============================================================

SELECT
    goal_name,
    ROUND(
        AVG(
            CASE
                WHEN target_amount > 0
                THEN (current_amount / target_amount) * 100
            END
        ),
        2
    ) AS average_goal_progress_percent
FROM SavingsGoal
GROUP BY goal_name
ORDER BY average_goal_progress_percent DESC;


-- 5.3 High-income customers with relatively low savings
--
-- Business question:
-- Which customers have above-average income but
-- below-average savings?
--
-- Use:
-- Creates a customer group that could be investigated
-- further in future analytical or AI models.
-- ============================================================

SELECT
    c.customer_id,
    c.age,
    c.income,
    c.customer_segment,
    ROUND(AVG(s.current_amount), 2) AS average_saved
FROM Customer c
JOIN SavingsGoal s
    ON c.customer_id = s.customer_id
WHERE c.income > (
    SELECT AVG(income)
    FROM Customer
)
GROUP BY
    c.customer_id,
    c.age,
    c.income,
    c.customer_segment
HAVING AVG(s.current_amount) < (
    SELECT AVG(current_amount)
    FROM SavingsGoal
)
ORDER BY average_saved ASC;


-- 5.4 Customers with both investments and savings goals
--
-- Business question:
-- How many customers are actively investing while
-- also maintaining savings goals?
--
-- Use:
-- Helps identify customers who use multiple financial
-- products.
-- ============================================================

SELECT
    c.customer_id,
    c.customer_segment,
    c.risk_profile,
    COUNT(DISTINCT i.investment_id) AS number_of_investments,
    COUNT(DISTINCT s.goal_id) AS number_of_savings_goals
FROM Customer c
LEFT JOIN Investment i
    ON c.customer_id = i.customer_id
LEFT JOIN SavingsGoal s
    ON c.customer_id = s.customer_id
GROUP BY
    c.customer_id,
    c.customer_segment,
    c.risk_profile
HAVING COUNT(DISTINCT i.investment_id) > 0
   AND COUNT(DISTINCT s.goal_id) > 0
ORDER BY number_of_investments DESC;


-- 5.5 Savings progress by customer segment
--
-- Business question:
-- How far have customers in each customer segment
-- progressed toward their savings goals?
--
-- Use:
-- Helps compare savings behavior between customer segments.
-- ============================================================

SELECT
    c.customer_segment,
    COUNT(s.goal_id) AS number_of_goals,
    ROUND(AVG(s.target_amount), 2) AS average_target,
    ROUND(AVG(s.current_amount), 2) AS average_saved,
    ROUND(
        AVG(
            (s.current_amount / NULLIF(s.target_amount, 0)) * 100
        ),
        2
    ) AS average_progress_percent
FROM Customer c
JOIN SavingsGoal s
    ON c.customer_id = s.customer_id
GROUP BY c.customer_segment
ORDER BY average_progress_percent DESC;


-- ============================================================
-- 6. MARKET DATA ANALYSIS
-- ============================================================


-- 6.1 Market data coverage by stock
--
-- Business question:
-- How much historical market data is available for each stock?
--
-- Use:
-- Helps validate the coverage of the market data used
-- in investment analysis.
-- ============================================================

SELECT
    ticker,
    COUNT(*) AS number_of_days,
    MIN(market_date) AS first_date,
    MAX(market_date) AS last_date
FROM MarketData
GROUP BY ticker
ORDER BY ticker;


-- 6.2 Latest stock price
--
-- Business question:
-- What is the latest available closing price for each stock?
--
-- Use:
-- Provides the current market price used in investment
-- valuation.
-- ============================================================

SELECT DISTINCT ON (ticker)
    ticker,
    market_date,
    close_price
FROM MarketData
ORDER BY ticker, market_date DESC;


-- ============================================================
-- 7. INVESTMENT PERFORMANCE ANALYSIS
-- ============================================================


-- 7.1 Current value of investments
--
-- Business question:
-- What is the current market value of each investment?
--
-- Calculation:
-- Current value = quantity × latest market price
--
-- Use:
-- Compares the original purchase value with the current
-- estimated market value.
-- ============================================================

SELECT
    i.investment_id,
    i.customer_id,
    i.ticker,
    i.sector,
    i.quantity,
    i.purchase_price,
    m.close_price AS current_price,
    ROUND(
        i.quantity * i.purchase_price,
        2
    ) AS purchase_value,
    ROUND(
        i.quantity * m.close_price,
        2
    ) AS current_value
FROM Investment i
JOIN (
    SELECT DISTINCT ON (ticker)
        ticker,
        close_price
    FROM MarketData
    ORDER BY ticker, market_date DESC
) m
    ON i.ticker = m.ticker
ORDER BY current_value DESC;


-- 7.2 Unrealized gain or loss
--
-- Business question:
-- Which investments currently have the largest
-- unrealized gains or losses?
--
-- Calculation:
-- Gain/loss = current value - purchase value
--
-- Use:
-- Provides an estimate of investment performance
-- based on the latest available market price.
-- ============================================================

SELECT
    i.customer_id,
    i.ticker,
    i.sector,
    ROUND(
        i.quantity * i.purchase_price,
        2
    ) AS purchase_value,
    ROUND(
        i.quantity * m.close_price,
        2
    ) AS current_value,
    ROUND(
        i.quantity * m.close_price
        - i.quantity * i.purchase_price,
        2
    ) AS gain_loss
FROM Investment i
JOIN (
    SELECT DISTINCT ON (ticker)
        ticker,
        close_price
    FROM MarketData
    ORDER BY ticker, market_date DESC
) m
    ON i.ticker = m.ticker
ORDER BY gain_loss DESC;


-- 7.3 Current investment value by sector
--
-- Business question:
-- Which sectors currently represent the largest
-- investment values?
--
-- Calculation:
-- Current value = quantity × latest market price
--
-- Use:
-- Shows the current sector exposure of customer investments.
-- ============================================================

SELECT
    i.sector,
    ROUND(
        SUM(i.quantity * m.close_price),
        2
    ) AS current_value
FROM Investment i
JOIN (
    SELECT DISTINCT ON (ticker)
        ticker,
        close_price
    FROM MarketData
    ORDER BY ticker, market_date DESC
) m
    ON i.ticker = m.ticker
GROUP BY i.sector
ORDER BY current_value DESC;