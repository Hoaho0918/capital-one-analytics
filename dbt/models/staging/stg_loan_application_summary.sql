{{ config(materialized='view') }}

with raw_source as (
    select * from {{ ref('base_flattened_data') }}
)

select
    -- Cross-Layer Verification Keys
    trim(cast("Account Activity.customer_id" as string)) as customer_id,
    
    -- Analytical Risk Profiling Tiers
    nullif(trim(cast("Customer Profile.risk_tolerance" as string)), '') as risk_tolerance,
    nullif(trim(cast("Customer Profile.investment_goals" as string)), '') as investment_goals,
    nullif(trim(cast("Customer Profile.financial_history" as string)), '') as financial_history,
    nullif(trim(cast("Customer Profile.sector" as string)), '') as institutional_sector,
    nullif(trim(cast("Customer Profile.income_level" as string)), '') as income_tier,
    
    -- Operational Thresholds & Status Flags
    cast("Account Activity.transaction_threshold" as float) as velocity_risk_threshold,
    nullif(trim(cast("Loan Application Summary.employment_status" as string)), '') as borrower_employment_status,
    upper(trim(cast("Loan Application Summary.loan_status" as string))) as loan_approval_status

from raw_source
where "Account Activity.customer_id" is not null
