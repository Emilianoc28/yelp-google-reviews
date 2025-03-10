from google.cloud import bigquery, storage
import pandas as pd
import json
import hashlib
from io import StringIO

# Configuración
BUCKET_NAME = "dataset-pf-gyelp"
TEMP_BUCKET_MAPS = "dataset-pf-gyelp/Yelp/airFlow/TEMP/MAPS"
FILES = {
    "metadata": "Google Maps/review-California/processed/metadata_cleaned.csv",
    "reviews": "Google Maps/review-California/processed/reviews_gm_cleaned.csv"
}
DATASET_NAME = "proyecto_dw"
TABLES = {
    "dim_business": "dim_business",
    "dim_category": "dim_category",
    "dim_city": "dim_city",
    "fact_reviews": "fact_reviews"
}

def generate_id(value):
    return hashlib.md5(value.encode()).hexdigest() if pd.notna(value) else None

def load_csv_from_gcs(bucket_name, file_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    data = blob.download_as_text()
    return pd.read_csv(StringIO(data))

def clear_temp_bucket(bucket_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    for blob in blobs:
        blob.delete()
    print(f"✅ Bucket {bucket_name} limpiado.")

def upload_to_gcs(bucket_name, file_name, df):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.upload_from_string(df.to_csv(index=False), content_type='text/csv')
    print(f"✅ Archivo {file_name} subido a {bucket_name}.")

def transform_and_load():
    client = bigquery.Client()
    
    # Limpiar bucket temporal
    clear_temp_bucket(TEMP_BUCKET_MAPS)
    
    # Cargar metadata
    df_metadata = load_csv_from_gcs(BUCKET_NAME, FILES["metadata"])
    df_reviews = load_csv_from_gcs(BUCKET_NAME, FILES["reviews"])
    
    # Generar IDs
    df_metadata["business_id"] = df_metadata["business_name"].apply(generate_id)
    df_metadata["city_id"] = df_metadata["city"].apply(generate_id)
    df_metadata["category_id"] = df_metadata["category"].apply(generate_id)
    
    # Validaciones
    print("Null values:\n", df_metadata.isnull().sum())
    
    # Subir archivos transformados al bucket TEMP
    upload_to_gcs(TEMP_BUCKET_MAPS, "metadata_transformed.csv", df_metadata)
    upload_to_gcs(TEMP_BUCKET_MAPS, "reviews_transformed.csv", df_reviews)
    
    # Carga a BigQuery
    for table, table_name in TABLES.items():
        table_ref = client.dataset(DATASET_NAME).table(table_name)
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=True,
        )
        df = df_metadata if table != "fact_reviews" else df_reviews
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        print(f"✅ Datos cargados en {table_name}")
    
if __name__ == "__main__":
    transform_and_load()
