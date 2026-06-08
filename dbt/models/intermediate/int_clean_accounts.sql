{{ config(materialized='view') }}

with staging_source as (
    select * from {{ ref('stg_account_activity') }}
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by account_id 
            order by activity_date desc
        ) as row_num
    from staging_source
)

select
    account_id,
    customer_id,
    upper(account_type) as account_type,
    
    -- Standardize negative ledger values to absolute zero where logical
    case 
        when current_balance >= -50000.00 then current_balance 
        else null 
    end as current_balance,
    
    deposit_amount,
    withdrawal_amount,
    transfer_amount,
    international_transfer_amount,
    market_investment_amount,
    velocity_risk_threshold,
    
    -- Standardize system timestamp parsing for chronology
    cast(activity_date as date) as activity_date

from deduplicated
where row_num = 1
