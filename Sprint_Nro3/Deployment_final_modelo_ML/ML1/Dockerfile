# Usar una imagen base con Python
FROM python:3.9

# Definir el directorio de trabajo en el contenedor
WORKDIR /ML1

# Copiar todos los archivos al contenedor
COPY . /ML1

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelos de NLP necesarios
RUN python -m nltk.downloader vader_lexicon
RUN python -m spacy download en_core_web_sm

# Exponer el puerto en el que corre Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "ML1.py", "--server.port=8501", "--server.address=0.0.0.0"]

