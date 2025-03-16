import streamlit as st
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_csv = os.path.join(BASE_DIR, "data_example", "top10_ciudad_ML2.csv")

# Verificar si el archivo existe
if not os.path.exists(ruta_csv):
    st.error(f"⚠ El archivo CSV no se encuentra en la ruta: {ruta_csv}")
    df = None
else:
    try:
        df = pd.read_csv(ruta_csv, encoding="utf-8", delimiter=",", quotechar='"')
        st.write("📌 Columnas del CSV:", df.columns.tolist())  # Mostrar columnas disponibles

        if "city" in df.columns:
            ciudades_disponibles = sorted(df["city"].dropna().unique())
        else:
            ciudades_disponibles = []
            st.warning("⚠ La columna 'city' no está en el archivo CSV.")
    except Exception as e:
        st.error(f"❌ Error al cargar el CSV: {e}")
        df = None
        ciudades_disponibles = []

st.set_page_config(page_title="Top Restaurantes en California", layout="wide")

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "inicio"

def volver_inicio():
    st.session_state.pagina_actual = "inicio"

if st.session_state.pagina_actual == "inicio":
    st.title("🌎 Mapa de Restaurantes en California")

    if df is not None and ciudades_disponibles:
        ciudad_seleccionada = st.selectbox("Selecciona una ciudad:", ciudades_disponibles)
    else:
        st.warning("⚠ No hay datos de ciudades disponibles.")
        ciudad_seleccionada = None  

    if st.button("🔍 Buscar restaurantes") and ciudad_seleccionada:
        st.session_state.pagina_actual = "resultados"
        st.session_state.ciudad_seleccionada = ciudad_seleccionada
        st.rerun()
