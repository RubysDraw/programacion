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
        return pd.read_csv(ARCHIVO)
    else:
        return pd.DataFrame(columns=[
            "Trabajador",
            "Tarea",
            "Lugar",
            "Fecha creación",
            "Fecha entrega",
            "Prioridad",
            "Estado"
        ])

def guardar_datos(df):
    df.to_csv(ARCHIVO, index=False)

# --------------------------------------------------
# Configuración
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
estado = st.sidebar.selectbox("📌 Estado", ["Pendiente", "En proceso", "Completado"])

if st.sidebar.button("Guardar tarea"):
    if trabajador and tarea and lugar:
        nueva = {
            "Trabajador": trabajador,
            "Tarea": tarea,
            "Lugar": lugar,
            "Fecha creación": date.today(),
            "Fecha entrega": fecha_entrega,
            "Prioridad": prioridad,
            "Estado": estado
        }
        df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
        guardar_datos(df)
        st.sidebar.success("✅ Tarea creada")
        st.experimental_rerun()

# --------------------------------------------------
# Filtros
# --------------------------------------------------
st.subheader("📋 Lista de tareas")

filtro_trabajador = st.selectbox(
    "Filtrar por trabajador",
    ["Todos"] + sorted(df["Trabajador"].dropna().unique().tolist())
)

filtro_estado = st.selectbox(
    "Filtrar por estado",
    ["Todos", "Pendiente", "En proceso", "Completado"]
)

filtro_prioridad = st.selectbox(
    "Filtrar por prioridad",
    ["Todos", "Alta", "Media", "Baja"]
)

df_filtrado = df.copy()

if filtro_trabajador != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Trabajador"] == filtro_trabajador]

if filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]

if filtro_prioridad != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Prioridad"] == filtro_prioridad]

df_filtrado = df_filtrado.reset_index(drop=False)

# --------------------------------------------------
# Tabla editable (SOLO Estado)
# --------------------------------------------------
st.markdown("✏️ **Puedes cambiar el estado directamente en la tabla**")

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
    use_container_width=True,
    key="tabla"
)

# --------------------------------------------------
# Guardar cambios SOLO si hay diferencias
# --------------------------------------------------
if not df_editor.equals(df_filtrado):
    for _, fila in df_editor.iterrows():
        df.loc[fila["index"], "Estado"] = fila["Estado"]
    guardar_datos(df)
    st.success("💾 Estado actualizado correctamente")

# --------------------------------------------------
# Tareas vencidas (visual)
# --------------------------------------------------
st.subheader("🔴 Tareas vencidas")

df["Fecha entrega"] = pd.to_datetime(df["Fecha entrega"], errors="coerce")

vencidas = df[
    (df["Estado"] != "Completado") &
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
        st.experimental_rerun()

# --------------------------------------------------
# Resumen
# --------------------------------------------------
st.subheader("📊 Resumen")

c1, c2, c3 = st.columns(3)
c1.metric("Pendientes", len(df[df["Estado"] == "Pendiente"]))
c2.metric("En proceso", len(df[df["Estado"] == "En proceso"]))
c3.metric("Completadas", len(df[df["Estado"] == "Completado"]))
