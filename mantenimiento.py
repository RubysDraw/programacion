import streamlit as st
import pandas as pd
from datetime import date
import os
from io import BytesIO

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

def exportar_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()

# ---------------------------
# Configuración Streamlit
# ---------------------------
st.set_page_config(page_title="Gestión de Mantenimiento", layout="wide")
st.title("🔧 Sistema de Gestión de Mantenimiento")

df = cargar_datos()

# ---------------------------
# Sidebar - Nueva tarea
# ---------------------------
st.sidebar.header("➕ Nueva tarea")

trabajador = st.sidebar.text_input("👷 Trabajador")
tarea = st.sidebar.text_area("📝 Tarea")
lugar = st.sidebar.text_input("📍 Lugar")
fecha_entrega = st.sidebar.date_input("📅 Fecha entrega", min_value=date.today())
estado = st.sidebar.selectbox("📌 Estado", ["Pendiente", "En proceso", "Completado"])

if st.sidebar.button("Guardar tarea"):
    if trabajador and tarea and lugar:
        nueva = {
            "Trabajador": trabajador,
            "Tarea": tarea,
            "Lugar": lugar,
            "Fecha creación": date.today(),
            "Fecha entrega": fecha_entrega,
            "Estado": estado
        }
        df = pd.concat([df, pd.DataFrame([nueva])], ignore_index=True)
        guardar_datos(df)
        st.sidebar.success("✅ Tarea creada")
        st.experimental_rerun()
    else:
        st.sidebar.error("❌ Completa todos los campos")

# ---------------------------
# Filtros (bloqueados)
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

df_filtrado = df_filtrado.reset_index()

# ---------------------------
# Tabla editable (solo Estado)
# ---------------------------
st.markdown("✏️ **Solo puedes modificar el estado de la tarea**")

df_editado = st.data_editor(
    df_filtrado,
    disabled=[
        "index",
        "Trabajador",
        "Tarea",
        "Lugar",
        "Fecha creación",
        "Fecha entrega"
    ],
    use_container_width=True,
    key="editor"
)

# Guardar cambios de estado
for _, fila in df_editado.iterrows():
    df.loc[fila["index"], "Estado"] = fila["Estado"]

guardar_datos(df)

# ---------------------------
# Eliminar tareas
# ---------------------------
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

# ---------------------------
# Exportar Excel
# ---------------------------
st.subheader("📤 Exportar")

st.download_button(
    label="📊 Descargar Excel",
    data=exportar_excel(df_filtrado.drop(columns=["index"])),
    file_name="tareas_mantenimiento.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------------------------
# Resumen
# ---------------------------
st.subheader("📊 Resumen")

c1, c2, c3 = st.columns(3)
c1.metric("🕒 Pendientes", len(df[df["Estado"] == "Pendiente"]))
c2.metric("⚙️ En proceso", len(df[df["Estado"] == "En proceso"]))
c3.metric("✅ Completadas", len(df[df["Estado"] == "Completado"]))
