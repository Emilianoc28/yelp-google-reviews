from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.sensors.pubsub import PubSubPullSensor
from datetime import datetime
from scripts.fetch import (
    clear_bucket_folder,
    fetch_google_restaurants,
    fetch_yelp_restaurants
)
from scripts.process import (transform_data, load_file_from_gcs)
from scripts.load import load_to_bigquery

# ConfiguraciÃƒÂ³n del DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 7, 10),
    "retries": 2,
}

dag = DAG(
    "etl_yelp_maps",
    default_args=default_args,
    description="Pipeline ETL para Yelp y Google Maps con Airflow",
    schedule_interval="*/7 * * * * ",
    catchup=False,
)

# Sensor Pub/Sub (espera mensaje del Google Cloud Scheduler)
pubsub_sensor_task = PubSubPullSensor(
    task_id="pubsub_sensor",
    project_id="proyectofinalgogleyelp",
    subscription="etl_yelp_maps",
    timeout=300,  # Espera hasta 5 min
    poke_interval=10,  # Revisa cada 30s
    mode="poke",  
    dag=dag,
)


# Limpiar carpetas antes de procesar
clear_raw_task = PythonOperator(
    task_id="clear_raw_folder",
    python_callable=lambda: clear_bucket_folder("Yelp/airFlow/raw/"),
    dag=dag,
)

# Obtener datos de APIs
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


# Procesar datos
process_task = PythonOperator(
    task_id="process_data",
    python_callable=transform_data,
    dag=dag,
)

clear_processed_task = PythonOperator(
    task_id="clear_processed_folder",
    python_callable=lambda: clear_bucket_folder("Yelp/airFlow/processed/"),
    dag=dag,
)
# Cargar datos en BigQuery
load_task = PythonOperator(
    task_id="load_to_bigquery",
    python_callable=load_to_bigquery,
    dag=dag,
)

# Definir flujo de ejecuciÃƒÂ³n
pubsub_sensor_task >> clear_raw_task >> [fetch_google_task, fetch_yelp_task] >> clear_processed_task >> process_task >> load_task
