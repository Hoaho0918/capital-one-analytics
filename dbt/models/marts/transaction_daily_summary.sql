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
    
    -- Operational Log Counts & Volumes
    count(distinct a.account_id) as impacted_accounts_count,
    sum(a.deposit_amount) as daily_aggregate_deposits,
    sum(a.withdrawal_amount) as daily_aggregate_withdrawals,
    sum(a.transaction_count) as aggregate_transaction_velocity_count,
    
    -- High-Risk Outflow Metrics
    sum(a.international_transfer_amount) as global_wire_outflow_volume,
    sum(a.repayment_amount) as aggregate_loan_debt_repayments,
    
    -- Risk Breach Evaluation Indicators
    count(distinct case when l.loan_status = 'APPROVED' then l.customer_id end) as active_borrower_count

from accounts a
left join loans l 
    on l.customer_id = (
        -- Links the transactional account data to the behavioral risk customer data
        select rs.customer_id 
        from {{ ref('stg_loan_application_summary') }} rs 
        limit 1
    )
group by 1, 2
