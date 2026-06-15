{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('int_clean_customers') }}
),

accounts as (
    select * from {{ ref('int_clean_accounts') }}
),

-- 1. Pull the bridge table to map account IDs to customer IDs properly
account_mapping as (
    select 
        account_id,
        customer_id
    from {{ ref('stg_loan_application_summary') }}
)

select
    -- Core Dimensions
    a.activity_date,
    m.customer_id,   -- Pulled from the mapping bridge
    c.occupation,
    c.region_code,

    -- Aggregated Financial Metrics
    count(distinct a.account_id) as active_accounts_count,
    sum(a.current_balance) as total_cash_balance,
    sum(a.deposit_amount) as total_deposits,
    sum(a.withdrawal_amount) as total_withdrawals,
    sum(a.transfer_amount + a.international_transfer_amount) as total_transfer_outflow_volume,
    sum(a.market_investment_amount) as active_market_exposure

from accounts a
-- 2. Link accounts to their specific customer_id via the bridge table
left join account_mapping m 
    on a.account_id = m.account_id
-- 3. Bring in customer details using the resolved customer_id
left join customers c 
    on m.customer_id = c.customer_id

group by 1, 2, 3, 4
