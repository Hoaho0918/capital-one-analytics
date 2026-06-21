
import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Add project root directory path to resolve custom python modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 1. Default task parameters configuration
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 2. Define the core operational DAG parameters
dag = DAG(
    'capital_one_financial_pipeline',
    default_args=default_args,
    description='End-to-end orchestration framework from raw landing zone files to gold analytical marts.',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1
)

# 3. Python Task Wrappers
def execute_bronze_ingestion():
    """Wrapper executing the raw file landing zone ingestion."""
    from src.ingestion.file_loader import ingest_to_bronze
    RAW_DATA_SOURCE = "data/bronze/sampleDataset.csv"
    BRONZE_LANDING_ZONE = "data/bronze/"
    ingest_to_bronze(RAW_DATA_SOURCE, BRONZE_LANDING_ZONE)

def execute_bronze_validation(**context):
    """Wrapper calling the data quality validation tests suite directly."""
    import uuid
    from src.quality.tests import initialize_audit_tables, run_bronze_checks
    initialize_audit_tables()
    
    # Generate a unique run ID and pass it downstream using Airflow XComs
    run_id = str(uuid.uuid4())
    context['ti'].xcom_push(key='pipeline_run_id', value=run_id)
    
    run_bronze_checks(run_id, "data/bronze/bronze_raw_landing.csv")

def execute_audit_logging(**context):
    """Appends final orchestration health run metadata rows to audit files."""
    from src.quality.tests import log_pipeline_run
    ti = context['ti']
    
    # Retrieve the unique run ID passed from the validation task via XCom
    run_id = ti.xcom_pull(task_ids='validate_bronze', key='pipeline_run_id')
    start_time = ti.start_date.isoformat()
    
    log_pipeline_run(run_id, "ORCHESTRATION_RUN", "SUCCESS", start_time)

# 4. Defining the Airflow Task Operator Components
task_ingest_csv_to_bronze = PythonOperator(
    task_id='ingest_csv_to_bronze',
    python_callable=execute_bronze_ingestion,
    dag=dag,
)

task_validate_bronze = PythonOperator(
    task_id='validate_bronze',
    python_callable=execute_bronze_validation,
    provide_context=True,
    dag=dag,
)

# Use dbt-cli selector flags to build modular stages without embedding SQL
task_run_dbt_staging = BashOperator(
    task_id='run_dbt_staging',
    bash_command='dbt run --select staging.*',
    cwd='/path/to/your/my_project/dbt_project',
    dag=dag,
)

task_run_dbt_silver = BashOperator(
    task_id='run_dbt_silver',
    bash_command='dbt run --select intermediate.*',
    cwd='/path/to/your/my_project/dbt_project',
    dag=dag,
)

task_run_dbt_gold = BashOperator(
    task_id='run_dbt_gold',
    bash_command='dbt run --select marts.*',
    cwd='/path/to/your/my_project/dbt_project',
    dag=dag,
)

task_write_audit = PythonOperator(
    task_id='write_audit',
    python_callable=execute_audit_logging,
    provide_context=True,
    dag=dag,
)

# 5. Enforce strict sequential order dependency paths
(
    task_ingest_csv_to_bronze 
    >> task_validate_bronze 
    >> task_run_dbt_staging 
    >> task_run_dbt_silver 
    >> task_run_dbt_gold 
    >> task_write_audit
)
