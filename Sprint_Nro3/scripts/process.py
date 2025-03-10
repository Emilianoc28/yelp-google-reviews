import pandas as pd
import numpy as np
from google.cloud import storage
from io import StringIO
import hashlib

# Configuración del bucket y rutas
BUCKET_NAME = "dataset-pf-gyelp"
PROCESSED_FOLDER = "Yelp/airFlow/processed"
TEMP_FOLDER = "Yelp/airFlow/TEMP"

def generate_md5(value):
    """Genera un hash MD5 para valores únicos."""
    return hashlib.md5(value.encode()).hexdigest()

def load_file_from_gcs(bucket, file_path):
    """Carga un archivo CSV desde GCS y lo convierte en un DataFrame de Pandas."""
    blob = bucket.blob(file_path)
    content = blob.download_as_text()
    return pd.read_csv(StringIO(content), encoding='utf-8')

def save_dataframe_to_gcs(bucket, df, file_name):
    """Guarda un DataFrame como CSV en TEMP dentro de GCS."""
    blob = bucket.blob(f"{TEMP_FOLDER}/YELP/{file_name}")
    content = df.to_csv(index=False)
    blob.upload_from_string(content, content_type="text/csv")
    print(f"✅ Guardado en TEMP: {file_name}")

def transform_data():
    """Carga archivos procesados, los transforma y los almacena en TEMP."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    # Archivos de entrada desde processed
    files = {
        "users_cleaned": f"{PROCESSED_FOLDER}/users_cleaned.csv",
        "reviews_cleaned": f"{PROCESSED_FOLDER}/reviews_cleaned.csv",
        "business_cleaned": f"{PROCESSED_FOLDER}/business_cleaned.csv",
        "tips_cleaned": f"{PROCESSED_FOLDER}/tips_cleaned.csv",
        "review_cleaned": f"{PROCESSED_FOLDER}/review_cleaned.csv"
    }

    # Cargar los archivos
    dataframes = {key: load_file_from_gcs(bucket, path) for key, path in files.items()}

    # 🔹 Tratamiento de valores nulos
    for name, df in dataframes.items():
        numeric_df = df.select_dtypes(include=[np.number])
        for col in numeric_df.columns:
            mean = df[col].mean()
            df[col].fillna(mean, inplace=True)
    print("✅ Valores nulos tratados correctamente.")
    
    # 🔹 Transformaciones
    users_cleaned = dataframes['users_cleaned'][['user_id', 'name', 'review_count', 'yelping_since']].copy()
    users_cleaned['yelping_since'] = pd.to_datetime(users_cleaned['yelping_since']).dt.date

    reviews_cleaned = dataframes['reviews_cleaned'][['review_id', 'business_id', 'user_id', 'stars', 'text', 'date']].copy()
    reviews_cleaned.rename(columns={'date': 'review_date'}, inplace=True)
    reviews_cleaned['review_date'] = pd.to_datetime(reviews_cleaned['review_date']).dt.date
    reviews_cleaned['stars'] = reviews_cleaned['stars'].astype(int)

    business_cleaned = dataframes['business_cleaned'][['business_id', 'name', 'address', 'city', 'categories', 'latitude', 'longitude', 'review_count']].copy()
    business_cleaned.rename(columns={'name': 'business_name'}, inplace=True)

    # 🔹 Normalización de ciudades y categorías
    cities = business_cleaned[['city']].drop_duplicates().copy()
    cities['city_id'] = cities['city'].apply(generate_md5)

    categories = business_cleaned[['categories']].drop_duplicates().copy()
    categories['category_id'] = categories['categories'].apply(generate_md5)

    business_cleaned = business_cleaned.merge(cities, on='city', how='left').drop(columns=['city'])
    business_cleaned = business_cleaned.merge(categories, on='categories', how='left').drop(columns=['categories'])

    # Diccionario con los datos transformados
    transformed_data = {
        "dim_user": users_cleaned,
        "fact_reviews": reviews_cleaned,
        "dim_business": business_cleaned,
        "dim_city": cities[['city_id', 'city']],
        "dim_category": categories.rename(columns={'categories': 'category'})
    }

    # Guardar archivos en TEMP
    for name, df in transformed_data.items():
        save_dataframe_to_gcs(bucket, df, f"{name}.csv")

    print("✅ Transformación completada y guardada en TEMP.")
