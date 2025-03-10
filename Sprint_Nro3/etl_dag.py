from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import transform
import load

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 9),
    'retries': 1,
}

dag = DAG(
    'etl_yelp',
    default_args=default_args,
    description='Pipeline ETL para Yelp con Airflow',
    schedule_interval='@weekly',
    catchup=False,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform.transform_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_datawarehouse',
    python_callable=load.load_to_datawarehouse,
    dag=dag,
)

transform_task >> load_task
