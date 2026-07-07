import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Import Cosmos engines for managing dbt transformations inside Snowflake
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, RenderConfig, TestBehavior
from cosmos.profiles import SnowflakeUserPasswordProfileMapping 

# 1. DYNAMIC PATH ROUTING (Multi-Environment Setup)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_ROOT)

DBT_PROJECT_PATH = os.path.join(PROJECT_ROOT, 'dbt')
BRONZE_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'bronze')

# 2. AIRFLOW DAG RULES CONFIGURATION
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'capital_one_financial_pipeline',
    default_args=default_args,
    description='Production-ready pipeline',
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1
)

# 3. CORE PYTHON OPERATION WRAPPERS
def execute_bronze_ingestion():
    from src.ingestion.file_loader import ingest_to_bronze
    raw_data_source = os.path.join(BRONZE_DATA_DIR, 'sampledataset.csv')
    ingest_to_bronze(raw_data_source, BRONZE_DATA_DIR)

def execute_bronze_validation(**context):
    import uuid
    from src.quality.tests import initialize_audit_tables, run_bronze_checks
    initialize_audit_tables()
    
    run_id = str(uuid.uuid4())
    context['ti'].xcom_push(key='pipeline_run_id', value=run_id)
    
    validation_target = os.path.join(BRONZE_DATA_DIR, 'bronze_raw_landing.csv')
    run_bronze_checks(run_id, validation_target)

def capture_silver_metrics(**context):
    from src.quality.tests import log_dbt_test_results
    ti = context['ti']
    run_id = ti.xcom_pull(task_ids='validate_bronze', key='pipeline_run_id')
    log_dbt_test_results(run_id, DBT_PROJECT_PATH, "SILVER")

def capture_gold_metrics(**context):
    from src.quality.tests import log_dbt_test_results
    ti = context['ti']
    run_id = ti.xcom_pull(task_ids='validate_bronze', key='pipeline_run_id')
    log_dbt_test_results(run_id, DBT_PROJECT_PATH, "GOLD")

def execute_audit_logging(**context):
    from src.quality.tests import log_pipeline_run
    ti = context['ti']
    run_id = ti.xcom_pull(task_ids='validate_bronze', key='pipeline_run_id')
    log_pipeline_run(run_id, "ORCHESTRATION_RUN", "SUCCESS", ti.start_date.isoformat())

# 4. INSTANTIATING THE PYTHON TASKS
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

task_audit_silver_metrics = PythonOperator(
    task_id='audit_silver_metrics',
    python_callable=capture_silver_metrics,
    provide_context=True,
    dag=dag,
)

task_audit_gold_metrics = PythonOperator(
    task_id='audit_gold_metrics',
    python_callable=capture_gold_metrics,
    provide_context=True,
    dag=dag,
)

task_write_audit = PythonOperator(
    task_id='write_audit',
    python_callable=execute_audit_logging,
    provide_context=True,
    dag=dag,
)

# 5. COSMOS PROFILE DESIGN FOR SNOWFLAKE CREDENTIALS
profile_config = ProfileConfig(
    profile_name="capital_one_snowflake",
    target_name="prod",
    profile_mapping=SnowflakeUserPasswordProfileMapping(
        conn_id="snowflake_production_conn"
    )
)

# 6. COSMOS TASK GROUPS WITH VISUAL TEST GATES
dbt_staging = DbtTaskGroup(
    group_id="dbt_staging_layer",
    project_config=ProjectConfig(DBT_PROJECT_PATH),
    profile_config=profile_config,
    render_config=RenderConfig(
        select=["path:models/staging"],
        test_behavior=TestBehavior.AFTER_EACH
    ), 
    dag=dag,
)

dbt_silver = DbtTaskGroup(
    group_id="dbt_silver_layer",
    project_config=ProjectConfig(DBT_PROJECT_PATH),
    profile_config=profile_config,
    render_config=RenderConfig(
        select=["path:models/intermediate"],
        test_behavior=TestBehavior.AFTER_EACH
    ),
    dag=dag,
)

dbt_gold = DbtTaskGroup(
    group_id="dbt_gold_layer",
    project_config=ProjectConfig(DBT_PROJECT_PATH),
    profile_config=profile_config,
    render_config=RenderConfig(
        select=["path:models/marts"],
        test_behavior=TestBehavior.AFTER_EACH
    ),
    dag=dag,
)

# 7. THE MASTER ASSEMBLY LINE DEPENDENCY PATH
(
    task_ingest_csv_to_bronze 
    >> task_validate_bronze 
    >> dbt_staging 
    >> dbt_silver 
    >> task_audit_silver_metrics 
    >> dbt_gold 
    >> task_audit_gold_metrics 
    >> task_write_audit
)
