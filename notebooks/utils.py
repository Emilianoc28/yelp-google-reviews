import os
import gdown
import pandas as pd
import json
import pyarrow.parquet as pq


def json_extract(drive_folder_url, local_folder):
    """
    Esta función extrae los archivos JSON de una carpeta en Google Drive y los almacena 
    localmente transformados a formato Parquet.

    Parámetros:
    - drive_folder_url (str): URL de la carpeta en Google Drive desde donde se extraerán los archivos JSON.
    - local_folder (str): Ruta local donde se almacenarán los archivos Parquet.

    La función descarga todos los archivos JSON de la carpeta de Google Drive y luego 
    convierte cada archivo a formato Parquet, almacenándolos en la carpeta local indicada.
    """

    # Paso 1: Extraer el listado de archivos desde Google Drive
    # Usamos gdown para descargar los archivos (requiere la URL del archivo, no de la carpeta)
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
    
    # Descargar todos los archivos JSON de la carpeta
    
    drive_files = gdown.download_folder(url=drive_folder_url, output="../data", quiet=False)
    
    for file_path in drive_files:
        if file_path.endswith('.json'):
        
            # Abre el archivo como texto
            with open(file_path, 'r', encoding='utf-8') as f:
                
                data = [json.loads(line) for line in f]  # Cargar cada línea como JSON
            # Intenta cargarlo manualmente
            try:
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    df = pd.json_normalize(data)
                parquet_file_path = os.path.join(local_folder, f'{os.path.basename(file_path).replace(".json", ".parquet")}')
                df.to_parquet(parquet_file_path)

                print(f"Archivo {file_path} convertido a Parquet y guardado como {parquet_file_path}")
            
            except Exception as e:
                print(f"Error al procesar el archivo {file_path}: {e}")


def download_file_from_drive(file_url, output_path):
    """
    Esta función descarga un archivo desde Google Drive usando el enlace directo del archivo.

    Parámetros:
    - file_url (str): URL directa del archivo en Google Drive.
    - output_path (str): Ruta local donde se guardará el archivo descargado.
    """
    try:
        # Descargar el archivo desde la URL de Google Drive
        gdown.download(file_url, output_path, quiet=False)
        print(f"Archivo descargado exitosamente y guardado en: {output_path}")
    except Exception as e:
        print(f"Error al descargar el archivo: {e}")




def data_summ_on_parquet(folder_path):
    '''
    Function to apply data_summ function to each Parquet file in a folder.

    Parameters:
    - folder_path (str): The path to the folder containing Parquet files.

    Returns:
    - summaries (list): A list of DataFrames containing the summary information for each Parquet file.
    '''
    summaries = []

    # Loop through each file in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Check if the file is a Parquet file
        if file_name.endswith('.parquet'):
            # Read the Parquet file into a DataFrame
            df = pq.read_table(file_path).to_pandas()

            # Get the title for the DataFrame based on the file name
            title = file_name.replace('.parquet', '')

            # Apply data_summ function to the DataFrame
            summary = data_summ(df, title=title)

            # Append the summary DataFrame to the list
            summaries.append(summary)
        # Check if the file is a pkl file
        elif file_name.endswith('.pkl'):
            # Read the pkl file into a DataFrame
            df = pd.read_pickle(file_path)

            # Get the title for the DataFrame based on the file name
            title = file_name.replace('.pkl', '')

            # Apply data_summ function to the DataFrame
            summary = data_summ(df, title=title)

            # Append the summary DataFrame to the list
            summaries.append(summary)

    return summaries

def data_summ(df, title=None):
    '''
    Function to provide detailed information about the dtype, null values,
    and outliers for each column in a DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame for which information is to be generated.
    - title (str, optional): Title to be used in the summary. If None, the title will be omitted.

    Returns:
    - df_info (pd.DataFrame): A DataFrame containing information about each column,
                              including data type, non-missing quantity, percentage of
                              missing values, missing quantity, and information about outliers.
    '''
    info_dict = {"Column": [], "Data_type": [], "No_miss_Qty": [], "%Missing": [], "Missing_Qty": []}

    for column in df.columns:
        info_dict["Column"].append(column)
        info_dict["Data_type"].append(df[column].apply(type).unique())
        info_dict["No_miss_Qty"].append(df[column].count())
        info_dict["%Missing"].append(round(df[column].isnull().sum() * 100 / len(df), 2))
        info_dict['Missing_Qty'].append(df[column].isnull().sum())

  
    df_info = pd.DataFrame(info_dict)

    if title:
        print(f"{title} Summary")
        print("\nTotal rows: ", len(df))
        print("\nTotal full null rows: ", df.isna().all(axis=1).sum())

    print(df_info.to_string(index=False))
    print("=====================================")

    return df_info
def calculate_original_memory_usage(main_folder_path):
    '''
    Function to calculate the total amount of memory usage
    by original dataframes files.

    Parameters:
    - main_folder_path: Path to the main folder containing original dataframe files.

    Returns:
    - Total memory usage in megabytes.
    '''

    # Initialize size variable to store total memory usage
    total_size = 0 

    # Loop through each DataFrame in the list
    for file_name in os.listdir(main_folder_path):

        if file_name.endswith('.json') or file_name.endswith('.pkl'):
            # Get the size of the file in megabytes and add to the total size
            file_path = os.path.join(main_folder_path, file_name)
            total_size += os.path.getsize(file_path)

    # Return the total memory usage
    return total_size


def calculate_parquet_memory_usage(main_folder_path):
    '''
    Function to calculate the total amount of memory usage
    by parquet files.

    Parameters:
    - main_folder_path: Path to the main folder containing parquet files.

    Returns:
    - Total memory usage in megabytes.
    '''
# Initialize size variable to store total memory usage
    total_size = 0 

    # Loop through each DataFrame in the list
    for file_name in os.listdir(main_folder_path):

        if file_name.endswith('.parquet'):
            # Get the size of the file in megabytes and add to the total size
            file_path = os.path.join(main_folder_path, file_name)
            total_size += os.path.getsize(file_path)

    # Return the total
    return total_size