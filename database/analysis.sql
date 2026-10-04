-- ============================================================
-- NORDIC BANK - AI & INVESTMENT ANALYTICS
-- SQL BUSINESS ANALYSIS
-- ============================================================

-- Database: PostgreSQL


-- ============================================================
-- 1. CUSTOMER ANALYSIS
-- ============================================================

-- 1.1 How are customers distributed across customer segments?

SELECT
    customer_segment,
    COUNT(*) AS number_of_customers
FROM Customer
GROUP BY customer_segment
ORDER BY number_of_customers DESC;


-- 1.2 How are customers distributed across risk profiles?

SELECT
    risk_profile,
    COUNT(*) AS number_of_customers
FROM Customer
GROUP BY risk_profile
ORDER BY number_of_customers DESC;


-- 1.3 Which customer segments have the highest average income?

SELECT
    customer_segment,
    ROUND(AVG(income), 2) AS average_income
FROM Customer
GROUP BY customer_segment
ORDER BY average_income DESC;


-- ============================================================
-- 2. ACCOUNT ANALYSIS
-- ============================================================

-- 2.1 What is the total balance held across all customer accounts?

SELECT
    ROUND(SUM(balance), 2) AS total_balance
FROM Account;


-- 2.2 How does the average account balance differ between customer segments?

SELECT
    c.customer_segment,
    COUNT(a.account_id) AS number_of_accounts,
    ROUND(AVG(a.balance), 2) AS average_balance
FROM Customer c
JOIN Account a
    ON c.customer_id = a.customer_id
GROUP BY c.customer_segment
ORDER BY average_balance DESC;


-- 2.3 How many accounts exist for each account type?

SELECT
    account_type,
    COUNT(*) AS number_of_accounts
FROM Account
GROUP BY account_type
ORDER BY number_of_accounts DESC;


-- ============================================================
-- 3. TRANSACTION ANALYSIS
-- ============================================================

-- 3.1 Which expense categories account for the largest transaction amounts?

SELECT
    category,
    COUNT(*) AS number_of_transactions,
    ROUND(SUM(amount), 2) AS total_amount
FROM Transactions
WHERE transaction_type = 'Expense'
GROUP BY category
ORDER BY total_amount DESC;


-- 3.2 What is the average transaction amount for each expense category?

SELECT
    category,
    ROUND(AVG(amount), 2) AS average_expense
FROM Transactions
WHERE transaction_type = 'Expense'
GROUP BY category
ORDER BY average_expense DESC;


-- 3.3 How do total income and total expenses compare?

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

-- 4.1 Which sectors represent the largest investment values?

SELECT
    sector,
    COUNT(*) AS number_of_investments,
    ROUND(SUM(quantity * purchase_price), 2) AS invested_amount
FROM Investment
GROUP BY sector
ORDER BY invested_amount DESC;


-- 4.2 How does investment activity differ between customer risk profiles?

SELECT
    c.risk_profile,
    COUNT(i.investment_id) AS number_of_investments,
    ROUND(SUM(i.quantity * i.purchase_price), 2) AS invested_amount
FROM Customer c
JOIN Investment i
    ON c.customer_id = i.customer_id
GROUP BY c.risk_profile
ORDER BY invested_amount DESC;


-- 4.3 Which customer segments have the largest investment values?

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

-- 5.1 What are the average target and saved amounts for different savings goals?

SELECT
    goal_name,
    COUNT(*) AS number_of_goals,
    ROUND(AVG(target_amount), 2) AS average_target,
    ROUND(AVG(current_amount), 2) AS average_saved
FROM SavingsGoal
GROUP BY goal_name
ORDER BY average_target DESC;


-- 5.2 How close are customers to reaching their savings goals?

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


-- 5.3 Which customers have above-average income but below-average savings?

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


-- 5.4 How many customers are actively investing while also maintaining savings goals?

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


-- 5.5 How far have customers in each customer segment progressed toward their savings goals?

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

-- 6.1 How much historical market data is available for each stock?

SELECT
    ticker,
    COUNT(*) AS number_of_days,
    MIN(market_date) AS first_date,
    MAX(market_date) AS last_date
FROM MarketData
GROUP BY ticker
ORDER BY ticker;


-- 6.2 What is the latest available closing price for each stock?

SELECT DISTINCT ON (ticker)
    ticker,
    market_date,
    close_price
FROM MarketData
ORDER BY ticker, market_date DESC;


-- ============================================================
-- 7. INVESTMENT PERFORMANCE ANALYSIS
-- ============================================================

-- 7.1 What is the current market value of each investment?

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


-- 7.2 Which investments currently have the largest unrealized gains or losses?

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


-- 7.3 Which sectors currently represent the largest investment values?

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