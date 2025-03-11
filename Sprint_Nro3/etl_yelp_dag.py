from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.fetch import (
    clear_bucket_folder,
    fetch_google_restaurants,
    fetch_yelp_restaurants
)
from scripts.process import transform_data
from scripts.load import load_to_bigquery

# Configuración del DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 7, 10),
    "retries": 5,
}

dag = DAG(
    "etl_yelp_maps",
    default_args=default_args,
    description="Pipeline ETL para Yelp y Google Maps con Airflow",
    schedule_interval="@weekly",
    catchup=False,
)

# 🧹 Limpiar carpetas antes de procesar
clear_raw_task = PythonOperator(
    task_id="clear_raw_folder",
    python_callable=lambda: clear_bucket_folder("Yelp/airFlow/raw/"),
    dag=dag,
)

# 📥 Obtener datos de APIs
fetch_google_task = PythonOperator(
    task_id="fetch_google_restaurants",
    python_callable=fetch_google_restaurants,
    dag=dag,
)

fetch_yelp_task = PythonOperator(
    task_id="fetch_yelp_restaurants",
    python_callable=fetch_yelp_restaurants,
    dag=dag,
)
clear_processed_task = PythonOperator(
    task_id="clear_processed_folder",
    python_callable=lambda: clear_bucket_folder("Yelp/airFlow/processed/"),
    dag=dag,
)

# 🔄 Procesar datos
process_task = PythonOperator(
    task_id="process_data",
    python_callable=transform_data,
    dag=dag,
)

# 🚀 Cargar datos en BigQuery
load_task = PythonOperator(
    task_id="load_to_bigquery",
    python_callable=load_to_bigquery,
    dag=dag,
)

# Definir flujo de ejecución
clear_raw_task >>[fetch_google_task, fetch_yelp_task] >> clear_processed_task >> process_task >>  load_task  
