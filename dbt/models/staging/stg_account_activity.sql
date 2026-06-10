{{ config(materialized='view') }}

with raw_source as (
    select * from {{ ref('base_flattened_data') }}
)

select
    -- Core Transactional Keys
    trim(cast("Account Activity.account_id" as string)) as account_id,
    nullif(trim(cast("Transaction Description" as string)), '') as transaction_description,
    nullif(trim(cast("Account Activity.account_type" as string)), '') as account_type,
    
    -- Cash Flows & Quantities
    cast("Account Activity.balance" as float) as current_balance,
    coalesce(cast("Account Activity.deposits" as float), 0.0) as deposit_amount,
    coalesce(cast("Account Activity.withdrawals" as float), 0.0) as withdrawal_amount,
    coalesce(cast("Account Activity.transfers" as float), 0.0) as transfer_amount,
    coalesce(cast("Account Activity.international_transfers" as float), 0.0) as international_transfer_amount,
    coalesce(cast("Account Activity.investments" as float), 0.0) as market_investment_amount,
    
    -- Loan Volumes & Time Series Metrics
    cast("Loan Application Summary.loan_amount" as float) as requested_loan_amount,
    nullif(trim(cast("Loan Application Summary.loan_purpose" as string)), '') as loan_purpose,
    cast("Loan Application Summary.loan_term" as integer) as loan_term_months,
    cast("Loan Application Summary.interest_rate" as float) as applied_interest_rate,
    coalesce(cast("Time Series Data.transactions" as integer), 0) as rolling_transaction_count,
    coalesce(cast("Time Series Data.repayments" as float), 0.0) as debt_repayment_amount,
    
    -- Rule 4 Chronological Anchor
    cast("Time Series Data.dates" as timestamp) as activity_date

from raw_source
where "Account Activity.account_id" is not null
