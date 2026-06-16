{{ config(materialized='table') }}

with customers as ( 
    select * from {{ ref('int_clean_customers') }} 
),

loans as ( 
    select * from {{ ref('int_clean_loans') }} 
),

-- STEP 1: Link raw accounts to loans to find the customer_id, 
-- then aggregate balances cleanly per individual customer.
customer_financial_summary as (
    select 
        l.customer_id,
        sum(a.current_balance) as total_savings_balance,
        sum(a.market_investment_amount) as total_investment_balance
    from {{ ref('int_clean_accounts') }} a
    left join loans l on a.account_id = l.account_id
    group by 1
)

select 
    -- 1, 2, 3, 4, 5: Cohort Segmentation Keys
    l.income_tier, 
    l.risk_tolerance_tier, 
    l.investment_goal, 
    c.education_level, 
    c.region_code, 

    -- Derived Demographic & Wealth Metrics
    count(distinct c.customer_id) as total_segmented_customers, 
    avg(c.customer_age) as average_segment_age, 
    avg(coalesce(a.total_savings_balance, 0.0)) as average_savings_balance, 
    avg(coalesce(a.total_investment_balance, 0.0)) as average_investment_balance, 

    -- Credit Risk & Application Summaries 
    sum(coalesce(l.velocity_risk_threshold, 0.0)) as total_allocated_risk_threshold, 
    count(distinct case when l.loan_status = 'APPROVED' then c.customer_id end) as approved_loan_applications_count, 
    count(distinct case when l.loan_status = 'DENIED' then c.customer_id end) as denied_loan_applications_count 

from customers c 
left join loans l 
    on c.customer_id = l.customer_id 
-- STEP 2: Safely join your financial aggregates using the true customer identity key
left join customer_financial_summary a 
    on c.customer_id = a.customer_id 

group by 1, 2, 3, 4, 5
