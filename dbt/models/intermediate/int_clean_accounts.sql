{{ config(materialized='view') }}

with staging_source as (
    select * from {{ ref('stg_account_activity') }}
),

deduplicated as (
    select
        *,
        -- Deduplicate by taking the latest transaction activity date per account
        row_number() over (
            partition by account_id 
            order by activity_date desc
        ) as row_num
    from staging_source
)

select
    account_id,
    initcap(transaction_description) as transaction_description,
    upper(account_type) as account_type,
    
    -- Validate financial bounds
    case 
        when current_balance >= -50000.00 then current_balance 
        else null 
    end as current_balance,
    
    deposit_amount,
    withdrawal_amount,
    transfer_amount,
    international_transfer_amount,
    market_investment_amount,
    
    -- Loan quantities belonging to the transactional footprint
    requested_loan_amount as loan_amount,
    upper(loan_purpose) as loan_purpose,
    loan_term_months,
    applied_interest_rate as interest_rate,
    
    rolling_transaction_count as transaction_count,
    debt_repayment_amount as repayment_amount,
    
    -- Standardize timestamp to a clean Date type
    cast(activity_date as date) as activity_date

from deduplicated
where row_num = 1
