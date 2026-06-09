# SCHEMA FREEZE
**File Source:** https://www.kaggle.com/datasets/s3r1alsh0ck/finance-dataset-for-fintech-applications

## Categorized Fields Matrix

### 1. Customer Fields
*Static, demographic, or identifying details of the entity.*
*   `Customer Profile.customer_id` (String) - Unique identifier linking demographics to the user.
*   `Customer Profile.age` (Integer) - Age of the account holder.
*   `Customer Profile.occupation` (String) - Profession or line of work.
*   `Customer Profile.education_level` (String) - Highest achieved educational tier.
*   `Customer Profile.marital_status` (String) - Legal marital state of the profile owner.
*   `Customer Profile.dependents` (Integer) - Total number of household dependents.
*   `Customer Profile.region` (String) - Geographic territory location classification.
*   `Customer Profile.employment_history` (String) - Past professional background logs.
*   `Customer Profile.address` (String) - Registered physical residence address.

### 2. Transaction Fields
*Core operational mechanics, balances, logs, and financial flows.*
*   `Transaction Description` (String) - Qualitative descriptor or label of the active event.
*   `Account Activity.account_id` (String) - Unique bank or investment account number.
*   `Account Activity.balance` (Float) - Current net cash balance inside the account.
*   `Account Activity.deposits` (Float) - Recorded positive cash inflows.
*   `Account Activity.withdrawals` (Float) - Recorded outbound cash liquidations.
*   `Account Activity.transfers` (Float) - Internal peer-to-peer asset shifts.
*   `Account Activity.international_transfers` (Float) - Cross-border outbound/inbound cash flows.
*   `Account Activity.investments` (Float) - Total asset value deployed into financial markets.
*   `Account Activity.account_type` (String) - Account tier type (e.g., Checking, Savings, Brokerage).
*   `Loan Application Summary.loan_amount` (Float) - Requested capital volume for funding.
*   `Loan Application Summary.loan_purpose` (String) - Stated utility for borrowing funds.
*   `Loan Application Summary.loan_term` (Integer) - Payback duration contract length (e.g., in months).
*   `Loan Application Summary.interest_rate` (Float) - Annualized borrowing cost yield percentage.
*   `Time Series Data.transactions` (Integer) - Sequential aggregation count of recent movements.
*   `Time Series Data.repayments` (Float) - Running value of paid principal or debt services.

### 3. Risk or Financial Behavior Fields
*Analytical tracking variables, safety triggers, risk profiles, and statuses.*
*   `Customer Profile.risk_tolerance` (String) - Assessed risk profile tier (e.g., Conservative, Aggressive).
*   `Customer Profile.investment_goals` (String) - Strategic wealth targets (e.g., Growth, Retirement).
*   `Customer Profile.financial_history` (String) - Qualitative track record summaries or credit tiers.
*   `Customer Profile.sector` (String) - Institutional business industry tracking alignment.
*   `Customer Profile.income_level` (String / Float) - Tracked economic capacity/earning bracket.
*   `Account Activity.customer_id` (String) - Secondary key used for tracking and cross-verifying profile consistency.
*   `Account Activity.transaction_threshold` (Float) - Set baseline cap monitoring safe/normal transfer velocity.
*   `Loan Application Summary.employment_status` (String) - Borrowing risk modifier verifying income stability.
*   `Loan Application Summary.loan_status` (String) - Credit resolution output (e.g., Approved, Denied, Pending).

### 4. Date/Time Fields
*System timestamps and execution logs utilized for chronological partitioning.*
*   `Time Series Data.dates` (Timestamp / Date) - Core operational timeline index tracking events.

---

## Raw Columns Matrix Configuration
*This programmatic contract explicitly locks down the structure for future ingestion layers:*

1. CUSTOMER: `['Customer Profile.customer_id', 'Customer Profile.age', 'Customer Profile.occupation', 'Customer Profile.education_level', 'Customer Profile.marital_status', 'Customer Profile.dependents', 'Customer Profile.region', 'Customer Profile.employment_history', 'Customer Profile.address']`
2. TRANSACTION: `['Transaction Description', 'Account Activity.account_id', 'Account Activity.balance', 'Account Activity.deposits', 'Account Activity.withdrawals', 'Account Activity.transfers', 'Account Activity.international_transfers', 'Account Activity.investments', 'Account Activity.account_type', 'Loan Application Summary.loan_amount', 'Loan Application Summary.loan_purpose', 'Loan Application Summary.loan_term', 'Loan Application Summary.interest_rate', 'Time Series Data.transactions', 'Time Series Data.repayments']`
3. RISK_BEHAVIOR: `['Customer Profile.risk_tolerance', 'Customer Profile.investment_goals', 'Customer Profile.financial_history', 'Customer Profile.sector', 'Customer Profile.income_level', 'Account Activity.customer_id', 'Account Activity.transaction_threshold', 'Loan Application Summary.employment_status', 'Loan Application Summary.loan_status']`
4. DATE_TIME: `['Time Series Data.dates']`
