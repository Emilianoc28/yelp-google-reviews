import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from PIL import Image
import os

# Obtener la ruta del archivo CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ruta_csv = os.path.join(BASE_DIR, "data_example", "top10_ciudad_ML2.csv")

# Verificar si el archivo existe
if not os.path.exists(ruta_csv):
    st.error(f"❌ El archivo CSV no existe en la ruta: {ruta_csv}")
    st.stop()

# Cargar el CSV con verificación de columnas
try:
    df = pd.read_csv(ruta_csv, encoding="utf-8", delimiter=",")
except Exception as e:
    st.error(f"❌ Error al cargar el CSV: {e}")
    st.stop()

# Limpiar nombres de columnas para evitar espacios o errores de mayúsculas
df.columns = df.columns.str.strip().str.lower()

# Verificar que la columna "city" existe
if "city" not in df.columns:
    st.error(f"❌ La columna 'city' no existe en el DataFrame. Columnas disponibles: {df.columns.tolist()}")
    st.stop()

# Configurar la interfaz
st.set_page_config(page_title="Top Restaurantes en California", layout="wide")

if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "inicio"

def volver_inicio():
    st.session_state.pagina_actual = "inicio"

if st.session_state.pagina_actual == "inicio":
    # Cargar imágenes
    logo_app_path = os.path.join(BASE_DIR, "Imagenes", "logo.jpg")
    logo_client_path = os.path.join(BASE_DIR, "Imagenes", "invertur.png")

    try:
        logo_app = Image.open(logo_app_path)
        logo_client = Image.open(logo_client_path)
    except Exception as e:
        st.warning(f"⚠ No se pudieron cargar las imágenes: {e}")

    # Diseño de la página
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.image(logo_app, width=150, caption="Insigh Labs")
    with col2:
        st.markdown("<h1 style='text-align: center;'>🌎 Mapa de Restaurantes en California</h1>", unsafe_allow_html=True)
    with col3:
        st.image(logo_client, width=150, caption="Invertur")

    # Selección de ciudad
    ciudad_seleccionada = st.selectbox("Selecciona una ciudad:", sorted(df["city"].dropna().unique()))

    # Botón de búsqueda
    if st.button("🔍 Buscar restaurantes"):
        st.session_state.pagina_actual = "resultados"
        st.session_state.ciudad_seleccionada = ciudad_seleccionada
        st.rerun()

elif st.session_state.pagina_actual == "resultados":
    ciudad_seleccionada = st.session_state.ciudad_seleccionada
    st.subheader(f"🏆 Top Restaurantes en {ciudad_seleccionada}")

    # Filtrar datos por ciudad y verificar si tiene coordenadas
    df_filtrado = df[df["city"] == ciudad_seleccionada].dropna(subset=["latitude", "longitude"])

    if df_filtrado.empty:
        st.warning("⚠ No hay datos disponibles para esta ciudad.")
    else:
        # Mostrar la tabla con los datos
        st.write(df_filtrado[["name", "address", "avg_rating", "num_of_reviews"]])

        # Calcular el centro del mapa
        latitud_media = df_filtrado["latitude"].mean()
        longitud_media = df_filtrado["longitude"].mean()

        # Crear el mapa
        mapa = folium.Map(location=[latitud_media, longitud_media], zoom_start=13)

        for _, row in df_filtrado.iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=f"{row['name']}\n📍 {row['address']}\n⭐ {row['avg_rating']} ({row['num_of_reviews']} reseñas)",
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(mapa)

        folium_static(mapa)

    if st.button("↩ Volver a la página principal"):
        volver_inicio()
        st.rerun()
