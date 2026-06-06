{{ config(materialized='view') }}

with raw_source as (
    select * from {{ ref('base_flattened_data') }}
)

select
    trim(cast("Customer Profile.customer_id" as string)) as customer_id,
    cast("Loan Application Summary.loan_amount" as float) as requested_loan_amount,
    cast("Loan Application Summary.loan_term" as integer) as loan_term_months,
    cast("Loan Application Summary.interest_rate" as float) as applied_interest_rate,
    
    -- Standardize statuses and flags
    nullif(trim(cast("Loan Application Summary.loan_purpose" as string)), '') as loan_purpose,
    nullif(trim(cast("Loan Application Summary.employment_status" as string)), '') as borrower_employment_status,
    nullif(trim(cast("Loan Application Summary.loan_status" as string)), '') as loan_approval_status,
    
    -- Include relevant aggregate metrics
    coalesce(cast("Time Series Data.transactions" as integer), 0) as rolling_transaction_count,
    coalesce(cast("Time Series Data.repayments" as float), 0.0) as debt_repayment_amount

from raw_source
where "Loan Application Summary.loan_amount" is not null
