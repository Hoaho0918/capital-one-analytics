{{ config(materialized='view') }}

with raw_source as (
    select * from {{ ref('base_flattened_data') }}
)

select
    trim(cast("Account Activity.account_id" as string)) as account_id,
    trim(cast("Account Activity.customer_id" as string)) as customer_id,
    nullif(trim(cast("Account Activity.account_type" as string)), '') as account_type,
    
    -- Cast financial balances and operational velocity thresholds
    cast("Account Activity.balance" as float) as current_balance,
    coalesce(cast("Account Activity.deposits" as float), 0.0) as deposit_amount,
    coalesce(cast("Account Activity.withdrawals" as float), 0.0) as withdrawal_amount,
    coalesce(cast("Account Activity.transfers" as float), 0.0) as transfer_amount,
    coalesce(cast("Account Activity.international_transfers" as float), 0.0) as international_transfer_amount,
    coalesce(cast("Account Activity.investments" as float), 0.0) as market_investment_amount,
    cast("Account Activity.transaction_threshold" as float) as velocity_risk_threshold,
    
    -- Clean timestamp parsing
    cast("Time Series Data.dates" as timestamp) as activity_date

from raw_source
where "Account Activity.account_id" is not null
