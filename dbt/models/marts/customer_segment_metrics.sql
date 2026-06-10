{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('int_clean_customers') }}
),

loans as (
    select * from {{ ref('int_clean_loans') }}
),

accounts_summary as (
    select 
        -- Group account metrics at the account type level to support the join structure
        account_type,
        sum(current_balance) as total_savings_balance,
        sum(market_investment_amount) as total_investment_balance
    from {{ ref('int_clean_accounts') }}
    group by 1
)

select
    -- Cohort Segmentation Keys (Now pulled cleanly from their correct frozen tables)
    l.income_tier,
    l.risk_tolerance_tier,
    l.investment_goal,
    c.education_level,
    c.region_code,
    
    -- Derived Demographic & Wealth Metrics
    count(distinct c.customer_id) as total_segmented_customers,
    avg(c.customer_age) as average_segment_age,
    avg(a.total_savings_balance) as average_savings_balance,
    avg(a.total_investment_balance) as average_investment_balance,
    
    -- Credit Risk & Application Summaries
    sum(coalesce(l.velocity_risk_threshold, 0.0)) as total_allocated_risk_threshold,
    count(distinct case when l.loan_status = 'APPROVED' then c.customer_id end) as approved_loan_applications_count,
    count(distinct case when l.loan_status = 'DENIED' then c.customer_id end) as denied_loan_applications_count

from customers c
left join loans l 
    on c.customer_id = l.customer_id
left join accounts_summary a 
    on l.employment_status is not null -- Joins aggregate financial context against risk profiles
group by 1, 2, 3, 4, 5
