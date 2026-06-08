{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('int_clean_customers') }}
),

accounts as (
    select * from {{ ref('int_clean_accounts') }}
)

select
    -- Dimensions
    a.activity_date,
    c.customer_id,
    c.occupation,
    c.region_code,
    
    -- Metrics
    count(distinct a.account_id) as active_accounts_count,
    sum(a.current_balance) as total_cash_balance,
    sum(a.deposit_amount) as total_deposits,
    sum(a.withdrawal_amount) as total_withdrawals,
    sum(a.transfer_amount + a.international_transfer_amount) as total_transfer_outflow_volume,
    sum(a.market_investment_amount) as active_market_exposure

from accounts a
left join customers c 
    on a.customer_id = c.customer_id
group by 1, 2, 3, 4
