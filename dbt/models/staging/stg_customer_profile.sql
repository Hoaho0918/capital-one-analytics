{{ config(materialized='view') }}

with raw_source as (
    select * from {{ ref('base_flattened_data') }}
)

select
    -- Primary Keys & Identifiers
    trim(cast("Customer Profile.customer_id" as string)) as customer_id,
    
    -- Demographic Attributes
    cast("Customer Profile.age" as integer) as customer_age,
    nullif(trim(cast("Customer Profile.occupation" as string)), '') as occupation,
    nullif(trim(cast("Customer Profile.education_level" as string)), '') as education_level,
    nullif(trim(cast("Customer Profile.marital_status" as string)), '') as marital_status,
    coalesce(cast("Customer Profile.dependents" as integer), 0) as dependent_count,
    nullif(trim(cast("Customer Profile.region" as string)), '') as region_code,
    nullif(trim(cast("Customer Profile.employment_history" as string)), '') as employment_history,
    nullif(trim(cast("Customer Profile.address" as string)), '') as physical_address

from raw_source
where "Customer Profile.customer_id" is not null
