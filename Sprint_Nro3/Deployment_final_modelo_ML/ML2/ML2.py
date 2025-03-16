import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from PIL import Image
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the CSV within the project
ruta_csv = os.path.join(BASE_DIR, "data_example", "top10_ciudad_ML2.csv")

# Load the CSV with pandas
df = pd.read_csv(ruta_csv, encoding="utf-8", delimiter=",", quotechar='"', header=None, names=["rating", "text"])

# Check if 'city' column exists before using it
if "city" in df.columns:
    ciudades_disponibles = sorted(df["city"].dropna().unique())
else:
    ciudades_disponibles = []  # No cities available

# Configure the app layout
st.set_page_config(page_title="Top Restaurantes en California", layout="wide")

# Session state for page navigation
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "inicio"

def volver_inicio():
    st.session_state.pagina_actual = "inicio"

# Home Page (City Selection)
if st.session_state.pagina_actual == "inicio":
    # Load images
    logo_app_path = os.path.join(BASE_DIR, "Imagenes", "logo.jpg")
    logo_client_path = os.path.join(BASE_DIR, "Imagenes", "invertur.png")

    logo_app = Image.open(logo_app_path)
    logo_client = Image.open(logo_client_path)

    # Align title and logos in a row
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.image(logo_app, width=150, caption="Insigh Labs")  
    with col2:
        st.markdown("<h1 style='text-align: center;'>🌎 Mapa de Restaurantes en California</h1>", unsafe_allow_html=True)
    with col3:
        st.image(logo_client, width=150, caption="Invertur")  

    # Select city (only if available)
    if ciudades_disponibles:
        ciudad_seleccionada = st.selectbox("Selecciona una ciudad:", ciudades_disponibles)
    else:
        st.warning("⚠ No hay datos de ciudades disponibles.")
        ciudad_seleccionada = None  

    # Search button
    if st.button("🔍 Buscar restaurantes") and ciudad_seleccionada:
        st.session_state.pagina_actual = "resultados"
        st.session_state.ciudad_seleccionada = ciudad_seleccionada
        st.rerun()

# Results Page (Table & Map)
elif st.session_state.pagina_actual == "resultados":
    ciudad_seleccionada = st.session_state.get("ciudad_seleccionada", None)

    if not ciudad_seleccionada:
        st.warning("⚠ Selecciona una ciudad primero.")
        volver_inicio()
        st.rerun()

    st.subheader(f"🏆 Top Restaurantes en {ciudad_seleccionada}")

    # Filter data by selected city (only if 'city' exists)
    if "city" in df.columns:
        df_filtrado = df[df["city"] == ciudad_seleccionada].dropna(subset=["latitude", "longitude"])
    else:
        df_filtrado = pd.DataFrame()  

    if df_filtrado.empty:
        st.warning("No hay datos disponibles para esta ciudad.")
    else:
        # Show table
        st.write(df_filtrado[["name", "address", "avg_rating", "num_of_reviews"]])

        # Calculate map center
        latitud_media = df_filtrado["latitude"].mean()
        longitud_media = df_filtrado["longitude"].mean()

        # Create map
        mapa = folium.Map(location=[latitud_media, longitud_media], zoom_start=13)

        # Add markers
        for _, row in df_filtrado.iterrows():
            nombre = row["name"]
            direccion = row["address"]
            puntuacion = row["avg_rating"]
            num_resenas = row["num_of_reviews"]
            lat, lon = row["latitude"], row["longitude"]

            folium.Marker(
                location=[lat, lon],
                popup=f"{nombre}\n📍 {direccion}\n⭐ {puntuacion} ({num_resenas} reseñas)",
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(mapa)

        # Display map
        folium_static(mapa)

    # Button to go back
    if st.button("↩ Volver a la página principal"):
        volver_inicio()
        st.rerun()
