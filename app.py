import streamlit as st
import pandas as pd
import json
import os
import hashlib

#from dotenv import load_dotenv
xload_dotenv()

st.set_page_config(page_title="Buscador de Proyectos", layout="wide")

# -------------------- AUTENTICACIÓN CON VARIABLES DE ENTORNO --------------------
USERNAME = os.getenv("APP_USERNAME")
PASSWORD = os.getenv("APP_PASSWORD")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Login")
    username_input = st.text_input("User:")
    password_input = st.text_input("Password:", type="password")

    if st.button("Iniciar Sesión"):
        if username_input == USERNAME and hash_password(password_input) == hash_password(PASSWORD):
            st.session_state["authenticated"] = True
            st.experimental_set_query_params(logged_in="true")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

if st.button("Cerrar Sesión"):
    st.session_state["authenticated"] = False
    st.experimental_set_query_params(logged_in="false")
    st.rerun()

# -------------------- RUTA DEL ARCHIVO LOCAL --------------------
RUTA_EXCEL = "/Users/jpocampo/Library/CloudStorage/OneDrive-CELSIAS.AE.S.P/Desarrollo de producto - 2. Seguimiento Leads SFV/Consolidado.xlsx"

def cargar_datos(ruta_excel):
    if not os.path.exists(ruta_excel):
        st.error("❌ No se encontró el archivo. Asegúrate de que está sincronizado desde OneDrive.")
        return pd.DataFrame()
    try:
        df = pd.read_excel(ruta_excel)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ Error al leer el archivo: {e}")
        return pd.DataFrame()

df = cargar_datos(RUTA_EXCEL)

# -------------------- BUSCADOR --------------------
st.title("🔍 Buscador de Proyectos")

if not df.empty:
    opcion_busqueda = st.radio("Buscar por:", ["Id", "Nombre de proyecto o Razón social"])
    valor = st.text_input("Ingresa el valor a buscar")

    df_filtrado = pd.DataFrame()
    if valor:
        df_filtrado = df[df[opcion_busqueda].astype(str).str.contains(valor.strip(), case=False)]

    if not df_filtrado.empty:
        for _, fila in df_filtrado.iterrows():
            with st.expander(f"📁 Proyecto: {fila.get('Nombre de proyecto o Razón social', 'Sin nombre')} (ID: {fila.get('Id', '-')})", expanded=True):
                for col in df.columns:
                    if col not in ["Id", "Nombre de proyecto o Razón social"] and pd.notna(fila[col]):
                        try:
                            valor_col = json.loads(fila[col])
                            if isinstance(valor_col, list) and all("link" in d for d in valor_col):
                                st.markdown(f"**{col}:**")
                                for doc in valor_col:
                                    nombre = doc.get("name", "Documento")
                                    link = doc.get("link")
                                    if link:
                                        st.markdown(f"- [📄 {nombre}]({link})", unsafe_allow_html=True)
                            else:
                                st.markdown(f"**{col}:** {fila[col]}")
                        except Exception:
                            st.markdown(f"**{col}:** {fila[col]}")
    else:
        if valor:
            st.warning("⚠️ No se encontraron resultados con ese criterio.")
else:
    st.stop()