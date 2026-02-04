import streamlit as st
import pandas as pd
from datetime import date
import os

ARCHIVO = "tareas.csv"

# --------------------------------------------------
# Funciones
# --------------------------------------------------
def cargar_datos():
    if os.path.exists(ARCHIVO):
        df = pd.read_csv(ARCHIVO)
        # Compatibilidad con CSV antiguo
        if "Cumplida" not in df.columns:
            df["Cumplida"] = False
    else:
        df = pd.DataFrame(columns=[
            "Trabajador",
            "Tarea",
            "Lugar",
            "Fecha creación",
            "Fecha entrega",
            "Prioridad",
            "Cumplida"
        ])
    return df

def guardar_datos(df):
    df.to_csv(ARCHIVO, index=False)

# --------------------------------------------------
# Configuración de la app
# --------------------------------------------------
st.set_page_config("Gestión de Mantenimiento", layout="wide")
st.title("🔧 Sistema de Gestión de Mantenimiento")

df = cargar_datos()

# --------------------------------------------------
# Sidebar - Nueva tarea
# --------------------------------------------------
st.sidebar.header("➕ Nueva tarea")

trabajador = st.sidebar.text_input("👷 Trabajador")
tarea = st.sidebar.text_area("📝 Tarea")
lugar = st.sidebar.text_input("📍 Lugar")
fecha_entrega = st.sidebar.date_input("📅 Fecha entrega", min_value=date.today())
prioridad = st.sidebar.selectbox("⭐ Prioridad", ["Alta", "Media", "Baja"])

if st.sidebar.button("Guardar tarea"):
    if trabajador and tarea and lugar:
        nueva = {
            "Trabajador": trabajador,
            "Tarea": tarea,
            "Lugar": lugar,
            "Fecha creación": date.today(),
            "Fecha entrega": fecha_entrega,
            "Prioridad": prioridad,
            "Cumplida": False
        }
        df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
        guardar_datos(df)
        st.sidebar.success("✅ Tarea creada")
        # Limpiar inputs
        trabajador = ""
        tarea = ""
        lugar = ""
        fecha_entrega = date.today()
        prioridad = "Media"
    else:
        st.sidebar.error("❌ Completa todos los campos")

# --------------------------------------------------
# Filtros compactos en una fila
# --------------------------------------------------
st.subheader("📋 Lista de tareas")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    filtro_trabajador = st.selectbox(
        "👷 Trabajador",
        ["Todos"] + sorted(df["Trabajador"].dropna().unique().tolist()),
        key="filtro_trabajador"
    )

with col2:
    filtro_prioridad = st.selectbox(
        "⭐ Prioridad",
        ["Todos", "Alta", "Media", "Baja"],
        key="filtro_prioridad"
    )

with col3:
    filtro_cumplida = st.selectbox(
        "☑️ Estado",
        ["Todas", "Cumplidas", "No cumplidas"],
        key="filtro_cumplida"
    )

df_filtrado = df.copy()

if filtro_trabajador != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Trabajador"] == filtro_trabajador]

if filtro_prioridad != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Prioridad"] == filtro_prioridad]

if filtro_cumplida == "Cumplidas":
    df_filtrado = df_filtrado[df_filtrado["Cumplida"] == True]
elif filtro_cumplida == "No cumplidas":
    df_filtrado = df_filtrado[df_filtrado["Cumplida"] == False]

df_filtrado = df_filtrado.reset_index(drop=False)

# --------------------------------------------------
# Tabla principal editable (solo Cumplida)
# --------------------------------------------------
st.markdown("☑️ **Marca la tarea como cumplida cuando esté terminada**")

df_editor = st.data_editor(
    df_filtrado,
    disabled=[
        "index",
        "Trabajador",
        "Tarea",
        "Lugar",
        "Fecha creación",
        "Fecha entrega",
        "Prioridad"
    ],
    column_config={
        "Cumplida": st.column_config.CheckboxColumn(
            "Cumplida",
            help="Marca si la tarea ya fue realizada"
        )
    },
    use_container_width=True,
    key="tabla"
)

# Guardar cambios automáticamente
if not df_editor.equals(df_filtrado):
    for _, fila in df_editor.iterrows():
        df.loc[fila["index"], "Cumplida"] = fila["Cumplida"]
    guardar_datos(df)
    st.success("💾 Cambios guardados")

# --------------------------------------------------
# Tareas vencidas
# --------------------------------------------------
st.subheader("🔴 Tareas vencidas")

df["Fecha entrega"] = pd.to_datetime(df["Fecha entrega"], errors="coerce")

vencidas = df[
    (df["Cumplida"] == False) &
    (df["Fecha entrega"].dt.date < date.today())
]

if len(vencidas) > 0:
    st.dataframe(vencidas, use_container_width=True)
else:
    st.success("No hay tareas vencidas 🎉")

# --------------------------------------------------
# Eliminar tarea
# --------------------------------------------------
st.subheader("🗑️ Eliminar tarea")

if len(df) > 0:
    fila_eliminar = st.selectbox(
        "Selecciona la tarea",
        df.index,
        format_func=lambda x: f"{df.loc[x, 'Trabajador']} | {df.loc[x, 'Tarea']}"
    )

    if st.button("❌ Eliminar tarea"):
        df = df.drop(fila_eliminar).reset_index(drop=True)
        guardar_datos(df)
        st.success("Tarea eliminada")

# --------------------------------------------------
# Resumen
# --------------------------------------------------
st.subheader("📊 Resumen")

c1, c2, c3 = st.columns(3)
c1.metric("📋 Totales", len(df))
c2.metric("✅ Cumplidas", len(df[df["Cumplida"] == True]))
c3.metric("⛔ Pendientes", len(df[df["Cumplida"] == False]))
