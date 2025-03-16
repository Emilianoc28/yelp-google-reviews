import streamlit as st
import pandas as pd

# URL del archivo CSV en GitHub Raw (asegúrate de cambiarla por la correcta)
url_csv = "https://raw.githubusercontent.com/usuario/repo/main/Sprint_Nro3/Deployment_final_modelo_ML/ML2/data_example/top10_ciudad_ML2.csv"

# Cargar el CSV
try:
    df = pd.read_csv(url_csv, encoding="utf-8", delimiter=",", quotechar='"')

    # Verificar si la columna "city" existe
    if "city" in df.columns:
        ciudades_disponibles = sorted(df["city"].dropna().unique())
    else:
        ciudades_disponibles = []  # No hay datos de ciudades

except Exception as e:
    st.error(f"Error al cargar el archivo CSV: {e}")
    df = pd.DataFrame()  # DataFrame vacío
    ciudades_disponibles = []

# Configuración de la página
st.set_page_config(page_title="Top Restaurantes en California", layout="wide")

# Estado de la sesión
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "inicio"

def volver_inicio():
    st.session_state.pagina_actual = "inicio"

# Página de inicio
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
