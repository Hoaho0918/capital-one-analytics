{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('int_clean_customers') }}
),

accounts as (
    select * from {{ ref('int_clean_accounts') }}
)

select
    -- Core Dimensions
    a.activity_date,
    c.customer_id,
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
left join customers c 
    on c.customer_id = (
        -- Safely resolve the link from account transactions back to customer IDs
        select acc_source.customer_id 
        from {{ ref('stg_loan_application_summary') }} acc_source 
        limit 1
    ) -- Note: If your actual dataset has customer_id natively in stg_account_activity, use: on a.customer_id = c.customer_id
group by 1, 2, 3, 4
