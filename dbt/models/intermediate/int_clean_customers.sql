{{ config(materialized='view') }}

with staging_source as (
    select * from {{ ref('stg_customer_profile') }}
),

deduplicated as (
    select
        *,
        -- Deduplicate by customer_id to guarantee unique records
        row_number() over (
            partition by customer_id 
            order by customer_id
        ) as row_num
    from staging_source
)

select
    customer_id,
    
    -- Validate numeric range for age (18 to 110)
    case 
        when customer_age between 18 and 110 then customer_age 
        else null 
    end as customer_age,
    
    -- Standardize string casing
    initcap(occupation) as occupation,
    initcap(education_level) as education_level,
    initcap(marital_status) as marital_status,
    dependent_count,
    
    -- Normalize region codes to uppercase
    upper(region_code) as region_code,
    employment_history,
    initcap(physical_address) as home_address

from deduplicated
where row_num = 1
