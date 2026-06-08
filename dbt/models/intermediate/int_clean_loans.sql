{{ config(materialized='view') }}

with staging_source as (
    select * from {{ ref('stg_loan_application_summary') }}
)

select
    customer_id,
    
    -- Validate numeric parameters
    case when requested_loan_amount > 0 then requested_loan_amount else 0.0 end as loan_amount,
    case when loan_term_months between 1 and 360 then loan_term_months else null end as loan_term_months,
    case when applied_interest_rate between 0.0 and 100.0 then applied_interest_rate else null end as interest_rate,
    
    -- Normalize codes and status buckets
    upper(loan_purpose) as loan_purpose,
    upper(borrower_employment_status) as employment_status,
    upper(loan_approval_status) as loan_status,
    
    rolling_transaction_count,
    debt_repayment_amount

from staging_source
