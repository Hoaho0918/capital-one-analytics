{{ config(materialized='table') }}

with accounts as (
    select * from {{ ref('int_clean_accounts') }}
),

loans as (
    select * from {{ ref('int_clean_loans') }}
)

select
    a.activity_date,
    a.account_type,
    
    -- Operational Volumes
    count(distinct a.account_id) as impacted_accounts_count,
    sum(a.deposit_amount) as daily_aggregate_deposits,
    sum(a.withdrawal_amount) as daily_aggregate_withdrawals,
    
    -- High-Risk Outflow Metrics
    sum(a.international_transfer_amount) as global_wire_outflow_volume,
    count(case when a.withdrawal_amount > a.velocity_risk_threshold then 1 end) as high_velocity_threshold_breaches,
    
    -- Debt Processing Contexts
    sum(coalesce(l.rolling_transaction_count, 0)) as aggregate_transaction_velocity_count,
    sum(coalesce(l.debt_repayment_amount, 0.0)) as aggregate_loan_debt_repayments

from accounts a
left join loans l 
    on a.customer_id = l.customer_id
group by 1, 2
