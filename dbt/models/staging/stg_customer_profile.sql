{{ config(materialized='view') }}

with raw_source as (
    select * from {{ ref('base_flattened_data') }}
)

select
    -- 1. Rename columns to clean, standardized snake_case
    trim(cast("Customer Profile.customer_id" as string)) as customer_id,
    cast("Customer Profile.age" as integer) as customer_age,
    
    -- 2. Trim strings and standardize empty values to NULL
    nullif(trim(cast("Customer Profile.occupation" as string)), '') as occupation,
    nullif(trim(cast("Customer Profile.education_level" as string)), '') as education_level,
    nullif(trim(cast("Customer Profile.marital_status" as string)), '') as marital_status,
    nullif(trim(cast("Customer Profile.region" as string)), '') as region,
    nullif(trim(cast("Customer Profile.address" as string)), '') as physical_address,
    
    -- 3. Behavioral and Risk fields casted properly for downstream metrics
    nullif(trim(cast("Customer Profile.risk_tolerance" as string)), '') as risk_tolerance_tier,
    nullif(trim(cast("Customer Profile.investment_goals" as string)), '') as investment_goal,
    nullif(trim(cast("Customer Profile.financial_history" as string)), '') as financial_history_tier,
    nullif(trim(cast("Customer Profile.sector" as string)), '') as employment_sector,
    nullif(trim(cast("Customer Profile.income_level" as string)), '') as income_tier,
    
    -- 4. Cast metrics and preserve lineage
    coalesce(cast("Customer Profile.dependents" as integer), 0) as dependent_count,
    cast(ingested_at as timestamp) as line_ingested_at,
    batch_id as pipeline_batch_id

from raw_source
where "Customer Profile.customer_id" is not null
