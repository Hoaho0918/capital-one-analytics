{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('int_clean_customers') }}
),

loans as (
    select * from {{ ref('int_clean_loans') }}
),

accounts as (
    select 
        customer_id,
        sum(current_balance) as total_savings_balance,
        sum(market_investment_amount) as total_investment_balance
    from {{ ref('int_clean_accounts') }}
    group by 1
)

select
    -- Cohort Segmentation Keys
    c.income_tier,
    c.risk_tolerance_tier,
    c.education_level,
    c.region_code,
    
    -- Derived Aggregate Metrics
    count(distinct c.customer_id) as total_segmented_customers,
    avg(c.customer_age) as average_segment_age,
    avg(a.total_savings_balance) as average_savings_balance,
    avg(a.total_investment_balance) as average_investment_balance,
    
    -- Credit Risk Summaries
    sum(coalesce(l.loan_amount, 0.0)) as total_outstanding_loan_principal,
    avg(coalesce(l.interest_rate, 0.0)) as average_applied_interest_rate,
    count(distinct case when l.loan_status = 'APPROVED' then c.customer_id end) as approved_loan_applications_count,
    count(distinct case when l.loan_status = 'DENIED' then c.customer_id end) as denied_loan_applications_count

from customers c
left join accounts a on c.customer_id = a.customer_id
left join loans l on c.customer_id = l.customer_id
group by 1, 2, 3, 4
