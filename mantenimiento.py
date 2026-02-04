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
    else:
        df = pd.DataFrame(columns=[
            "Trabajador",
            "Tarea",
            "Lugar",
            "Fecha creación",
            "Fecha entrega",
            "Prioridad",
            "Estado"
        ])
    return df

def guardar_datos(df):
    df.to_csv(ARCHIVO, index=False)

# --------------------------------------------------
# Configuración Streamlit
# --------------------------------------------------
st.set_page_config(page_title="Gestión de Mantenimiento", layout="wide")
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
    else:
        st.sidebar.error("❌ Completa todos los campos")

# --------------------------------------------------
# Filtros (bloqueados)
# --------------------------------------------------
st.subheader("📋 Lista de tareas")

col1, col2, col3 = st.columns(3)

with col1:
    filtro_trabajador = st.selectbox(
        "Filtrar por trabajador",
        ["Todos"] + sorted(df["Trabajador"].dropna().unique().tolist())
    )

with col2:
    filtro_estado = st.selectbox(
        "Filtrar por estado",
        ["Todos", "Pendiente", "En proceso", "Completado"]
    )

with col3:
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

# --------------------------------------------------
# Preparar datos (fechas y vencidas)
# --------------------------------------------------
df_filtrado = df_filtrado.reset_index()

df_filtrado["Fecha entrega"] = pd.to_datetime(df_filtrado["Fecha entrega"])

df_filtrado["Vencida"] = (
    (df_filtrado["Fecha entrega"].dt.date < date.today()) &
    (df_filtrado["Estado"] != "Completado")
)

# --------------------------------------------------
# Tabla editable (solo Estado)
# --------------------------------------------------
st.markdown("✏️ **Solo puedes modificar el estado de la tarea**")

df_mostrar = df_filtrado.drop(columns=["Vencida"])

df_editado = st.data_editor(
    df_mostrar,
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
    key="editor"
)

# Guardar cambios de estado
for _, fila in df_editado.iterrows():
    df.loc[fila["index"], "Estado"] = fila["Estado"]

guardar_datos(df)

# --------------------------------------------------
# Indicador visual de tareas vencidas
# --------------------------------------------------
st.markdown("### 🔴 Tareas vencidas")

vencidas = df_filtrado[df_filtrado["Vencida"]]

if len(vencidas) > 0:
    st.dataframe(
        vencidas.drop(columns=["Vencida", "index"]),
        use_container_width=True
    )
else:
    st.success("No hay tareas vencidas 🎉")

# --------------------------------------------------
# Eliminar tareas
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
else:
    st.info("No hay tareas para eliminar")

# --------------------------------------------------
# Resumen
# --------------------------------------------------
st.subheader("📊 Resumen")

c1, c2, c3, c4 = st.columns(4)
c1.metric("🕒 Pendientes", len(df[df["Estado"] == "Pendiente"]))
c2.metric("⚙️ En proceso", len(df[df["Estado"] == "En proceso"]))
c3.metric("✅ Completadas", len(df[df["Estado"] == "Completado"]))
c4.metric(
    "⛔ Vencidas",
    len(df[
        (df["Estado"] != "Completado") &
        (pd.to_datetime(df["Fecha entrega"]).dt.date < date.today())
    ])
)
