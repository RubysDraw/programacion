import streamlit as st
import pandas as pd
from datetime import date
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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

def exportar_pdf(df):
    c = canvas.Canvas("tareas_mantenimiento.pdf", pagesize=A4)
    text = c.beginText(40, 800)
    text.setFont("Helvetica", 9)

    for i, row in df.iterrows():
        linea = f"{row['Trabajador']} | {row['Tarea']} | {row['Lugar']} | {row['Fecha entrega']} | {row['Estado']}"
        text.textLine(linea)
        if text.getY() < 40:
            c.drawText(text)
            c.showPage()
            text = c.beginText(40, 800)
            text.setFont("Helvetica", 9)

    c.drawText(text)
    c.save()

# ---------------------------
# Configuración
# ---------------------------
st.set_page_config("Gestión de Mantenimiento", layout="wide")
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

# ---------------------------
# Filtros (NO editables)
# ---------------------------
st.subheader("📋 Tareas")

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

df_filtrado = df_filtrado.reset_index(drop=True)

# ---------------------------
# Editor de tabla (solo Estado editable)
# ---------------------------
st.markdown("✏️ **Solo puedes cambiar el estado**")

df_editado = st.data_editor(
    df_filtrado,
    disabled=["Trabajador", "Tarea", "Lugar", "Fecha creación", "Fecha entrega"],
    use_container_width=True,
    key="editor"
)

# Guardar cambios de estado
df.update(df_editado)
guardar_datos(df)

# ---------------------------
# Eliminar tareas
# ---------------------------
st.subheader("🗑️ Eliminar tarea")

fila_eliminar = st.selectbox(
    "Selecciona la tarea a eliminar",
    df.index,
    format_func=lambda x: f"{df.loc[x, 'Trabajador']} - {df.loc[x, 'Tarea']}"
)

if st.button("❌ Eliminar tarea"):
    df = df.drop(fila_eliminar).reset_index(drop=True)
    guardar_datos(df)
    st.success("Tarea eliminada")
    st.experimental_rerun()

# ---------------------------
# Exportar
# ---------------------------
st.subheader("📤 Exportar")

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "📊 Descargar Excel",
        data=df_filtrado.to_excel(index=False, engine="openpyxl"),
        file_name="tareas_mantenimiento.xlsx"
    )

with col2:
    if st.button("📄 Generar PDF"):
        exportar_pdf(df_filtrado)
        st.success("PDF generado: tareas_mantenimiento.pdf")

# ---------------------------
# Resumen
# ---------------------------
st.subheader("📊 Resumen")
c1, c2, c3 = st.columns(3)

c1.metric("Pendientes", len(df[df["Estado"] == "Pendiente"]))
c2.metric("En proceso", len(df[df["Estado"] == "En proceso"]))
c3.metric("Completadas", len(df[df["Estado"] == "Completado"]))
