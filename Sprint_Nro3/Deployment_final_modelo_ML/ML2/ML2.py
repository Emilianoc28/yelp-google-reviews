import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from PIL import Image


# Cargar el dataset limpio
ruta_csv = r"D:\Soy Henry\Proyecto Final\yelp-google-reviews\Sprint_Nro3\Deployment_final_modelo_ML\data_example\top10_ciudad_ML2.csv"  # Asegúrate de que la ruta sea correcta
df = pd.read_csv(ruta_csv)

# Configurar la interfaz de la aplicación
st.set_page_config(page_title="Top Restaurantes en California", layout="wide")

# Estado de sesión para controlar las vistas
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "inicio"

def volver_inicio():
    st.session_state.pagina_actual = "inicio"

# Página de inicio (selección de ciudad)
if st.session_state.pagina_actual == "inicio":
    # Cargar imágenes
    logo_app = Image.open("D:/Soy Henry/Proyecto Final/yelp-google-reviews/Imagenes/logo.jpg")
    logo_client = Image.open("D:/Soy Henry/Proyecto Final/yelp-google-reviews/Imagenes/invertur.png")

    # Usar columnas para alinear el título y los logos en una fila
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.image(logo_app, width=150, caption='Insigh Labs')  # Logo ampliado
    with col2:
        st.markdown("<h1 style='text-align: center;'>🌎 Mapa de Restaurantes en California</h1>", unsafe_allow_html=True)
    with col3:
        st.image(logo_client, width=150, caption='Invertur')  # Logo ampliado


    # Selección de ciudad
    ciudades_disponibles = sorted(df["city"].dropna().unique())  # Filtrar valores nulos
    ciudad_seleccionada = st.selectbox("Selecciona una ciudad:", ciudades_disponibles)

    # Botón de búsqueda
    if st.button("🔍 Buscar restaurantes"):
        st.session_state.pagina_actual = "resultados"
        st.session_state.ciudad_seleccionada = ciudad_seleccionada
        st.rerun()

# Página de resultados (tabla y mapa)
elif st.session_state.pagina_actual == "resultados":
    ciudad_seleccionada = st.session_state.ciudad_seleccionada

    st.subheader(f"🏆 Top Restaurantes en {ciudad_seleccionada}")

    # Filtrar datos de la ciudad seleccionada
    df_filtrado = df[df["city"] == ciudad_seleccionada].dropna(subset=["latitude", "longitude"])

    if df_filtrado.empty:
        st.warning("No hay datos disponibles para esta ciudad.")
    else:
        # Mostrar la tabla con los datos
        st.write(df_filtrado[["name", "address", "avg_rating", "num_of_reviews"]])

        # Calcular el centro promedio de los puntos para centrar el mapa
        latitud_media = df_filtrado["latitude"].mean()
        longitud_media = df_filtrado["longitude"].mean()

        # Crear el mapa centrado en la ciudad seleccionada
        mapa = folium.Map(location=[latitud_media, longitud_media], zoom_start=13)

        # Agregar marcadores de los restaurantes en el mapa
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

        # Mostrar el mapa debajo de la tabla
        folium_static(mapa)

    # Botón para volver a la página principal
    if st.button("↩ Volver a la página principal"):
        volver_inicio()
        st.rerun()
