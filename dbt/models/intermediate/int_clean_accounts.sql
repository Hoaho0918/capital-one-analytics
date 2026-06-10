{{ config(materialized='view') }}

with staging_source as (
    select * from {{ ref('stg_loan_application_summary') }}
)

select
    customer_id,
    
    -- Normalize risk categories and flags to standard uppercase
    upper(risk_tolerance) as risk_tolerance_tier,
    initcap(investment_goals) as investment_goal,
    upper(financial_history) as financial_history_tier,
    upper(institutional_sector) as employment_sector,
    upper(income_tier) as income_tier,
    
    velocity_risk_threshold,
    upper(borrower_employment_status) as employment_status,
    upper(loan_approval_status) as loan_status

from staging_source
