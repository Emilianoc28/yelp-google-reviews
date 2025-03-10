from google.cloud import bigquery
from google.cloud import storage

# Configuración del bucket y Data Warehouse
BUCKET_NAME = "dataset-pf-gyelp"
TEMP_FOLDER = "Yelp/airFlow/TEMP"
DATASET_NAME = "yelp_dataset"

def load_to_datawarehouse():
    """Carga los archivos de TEMP en el Data Warehouse (BigQuery)."""
    client = bigquery.Client()
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    # Definir las tablas destino en BigQuery
    tables = {
        "dim_user": "dim_user",
        "fact_reviews": "fact_reviews",
        "dim_business": "dim_business",
        "dim_city": "dim_city",
        "dim_category": "dim_category"
    }

    dataset_ref = client.dataset(DATASET_NAME)

    for table_name, table_id in tables.items():
        file_path = f"{TEMP_FOLDER}/{table_name}.csv"
        blob = bucket.blob(file_path)

        if blob.exists():
            uri = f"gs://{BUCKET_NAME}/{file_path}"
            table_ref = dataset_ref.table(table_id)

            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                autodetect=True
            )

            try:
                load_job = client.load_table_from_uri(uri, table_ref, job_config=job_config)
                load_job.result()  # Espera la carga
                print(f"✅ Cargado en BigQuery: {table_id}")
            except Exception as e:
                print(f"❌ Error cargando {table_id}: {e}")

        else:
            print(f"⚠️ Archivo no encontrado en TEMP: {file_path}")
