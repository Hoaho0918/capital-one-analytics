{{ config(materialized='view') }}

with staging_source as (
    select * from {{ ref('stg_customer_profile') }}
),

deduplicated as (
    select
        *,
        -- Deduplicate by taking the latest customer profile metadata record
        row_number() over (
            partition by customer_id 
            order by line_ingested_at desc
        ) as row_num
    from staging_source
)

select
    customer_id,
    
    -- Validate numeric range for age (cap outliers or corrupt system entry text strings)
    case 
        when customer_age between 18 and 110 then customer_age
        else null 
    end as customer_age,
    
    -- Standardize formatting rules to title casing
    initcap(occupation) as occupation,
    initcap(education_level) as education_level,
    initcap(marital_status) as marital_status,
    
    -- Normalize regional entries into clean uppercase codes
    upper(region) as region_code,
    physical_address,
    
    -- Preserve risk parameters for downstream risk profiles
    risk_tolerance_tier,
    investment_goal,
    financial_history_tier,
    employment_sector,
    income_tier,
    dependent_count

from deduplicated
where row_num = 1  -- Removes duplicates
