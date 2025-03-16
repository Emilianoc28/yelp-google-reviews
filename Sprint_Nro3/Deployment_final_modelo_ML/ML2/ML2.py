import streamlit as st
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_csv = os.path.join(BASE_DIR, "data_example", "top10_ciudad_ML2.csv")

# Load CSV
df = pd.read_csv(ruta_csv, encoding="utf-8", delimiter=",", quotechar='"', header=None, names=["rating", "text"])

# Check if 'city' column exists
if "city" in df.columns:
    ciudades_disponibles = sorted(df["city"].dropna().unique())
else:
    ciudades_disponibles = []  # No city data

st.set_page_config(page_title="Top Restaurantes en California", layout="wide")

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "inicio"

def volver_inicio():
    st.session_state.pagina_actual = "inicio"

if st.session_state.pagina_actual == "inicio":
    st.title("🌎 Mapa de Restaurantes en California")

    if ciudades_disponibles:
        ciudad_seleccionada = st.selectbox("Selecciona una ciudad:", ciudades_disponibles)
    else:
        st.warning("⚠ No hay datos de ciudades disponibles.")
        ciudad_seleccionada = None  

    if st.button("🔍 Buscar restaurantes") and ciudad_seleccionada:
        st.session_state.pagina_actual = "resultados"
        st.session_state.ciudad_seleccionada = ciudad_seleccionada
        st.rerun()
