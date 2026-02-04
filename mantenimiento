import streamlit as st
import pandas as pd
from datetime import date
import os

ARCHIVO = "tareas.csv"

# ---------------------------
# Funciones
# ---------------------------
def cargar_datos():
    if os.path.exists(ARCHIVO):
        return pd.read_csv(ARCHIVO)
    else:
        return pd.DataFrame(columns=[
            "Trabajador",
            "Tarea",
            "Lugar",
            "Fecha creación",
            "Fecha entrega",
            "Estado"
        ])

def guardar_datos(df):
    df.to_csv(ARCHIVO, index=False)

# ---------------------------
# Configuración Streamlit
# ---------------------------
st.set_page_config(page_title="Gestión de Mantenimiento", layout="wide")
st.title("🔧 Sistema de Gestión de Mantenimiento")

# ---------------------------
# Cargar datos
# ---------------------------
df = cargar_datos()

# ---------------------------
# Sidebar - Crear tarea
# ---------------------------
st.sidebar.header("➕ Nueva tarea")

trabajador = st.sidebar.text_input("👷 Trabajador")
tarea = st.sidebar.text_area("📝 Descripción de la tarea")
lugar = st.sidebar.text_input("📍 Lugar")
fecha_entrega = st.sidebar.date_input("📅 Fecha de entrega", min_value=date.today())
estado = st.sidebar.selectbox("📌 Estado", ["Pendiente", "En proceso", "Completado"])

if st.sidebar.button("Guardar tarea"):
    if trabajador and tarea and lugar:
        nueva_fila = {
            "Trabajador": trabajador,
            "Tarea": tarea,
            "Lugar": lugar,
            "Fecha creación": date.today(),
            "Fecha entrega": fecha_entrega,
            "Estado": estado
        }
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        guardar_datos(df)
        st.sidebar.success("✅ Tarea guardada correctamente")
    else:
        st.sidebar.error("❌ Completa todos los campos")

# ---------------------------
# Filtros
# ---------------------------
st.subheader("📋 Lista de tareas")

col1, col2 = st.columns(2)

with col1:
    filtro_trabajador = st.selectbox(
        "Filtrar por trabajador",
        ["Todos"] + sorted(df["Trabajador"].unique().tolist())
    )

with col2:
    filtro_estado = st.selectbox(
        "Filtrar por estado",
        ["Todos", "Pendiente", "En proceso", "Completado"]
    )

df_filtrado = df.copy()

if filtro_trabajador != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Trabajador"] == filtro_trabajador]

if filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]

# ---------------------------
# Mostrar tabla
# ---------------------------
st.dataframe(df_filtrado, use_container_width=True)

# ---------------------------
# Estadísticas rápidas
# ---------------------------
st.subheader("📊 Resumen")
col1, col2, col3 = st.columns(3)

col1.metric("🕒 Pendientes", len(df[df["Estado"] == "Pendiente"]))
col2.metric("⚙️ En proceso", len(df[df["Estado"] == "En proceso"]))
col3.metric("✅ Completadas", len(df[df["Estado"] == "Completado"]))
