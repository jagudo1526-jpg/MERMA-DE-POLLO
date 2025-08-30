import streamlit as st
import pandas as pd
import io
from pathlib import Path

# ---------- Configuración ----------
st.set_page_config(page_title="Control de Merma - Pollo Entero", layout="centered")

# ---------- Estilos (azul & amarillo) ----------
st.markdown("""
    <style>
        h1, h2, h3 { color: #1a3d7c; }
        div.stButton > button {
            background-color: #f1c40f; color: black; border-radius: 10px; border: none; font-weight: bold;
        }
        div.stButton > button:hover { background-color: #d4ac0d; color: white; }
    </style>
""", unsafe_allow_html=True)

# ---------- Encabezado con logo seguro ----------
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    logo_path = Path("logo.png")
    if logo_path.exists():
        st.image(str(logo_path), width=120)
    else:
        st.caption("Sube **logo.png** a la carpeta para mostrar el logo.")
with col_titulo:
    st.markdown("<h1 style='margin-top: 15px;'>🐔 Control de Merma - Pollo Entero</h1>", unsafe_allow_html=True)

st.divider()

# ---------- Estado de sesión ----------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Cliente", "Peso vendido (kg)"])
if "peso_inicial" not in st.session_state:
    st.session_state.peso_inicial = 0.0
if "peso_devolucion" not in st.session_state:
    st.session_state.peso_devolucion = 0.0

# ---------- Entradas ----------
st.subheader("📥 Registro de Ventas y Devoluciones")

st.session_state.peso_inicial = st.number_input(
    "⚖️ Peso inicial del pollo (kg)", min_value=0.0, step=0.01, value=st.session_state.peso_inicial
)

with st.form("form_ventas", clear_on_submit=True):
    cliente = st.text_input("👤 Nombre del cliente").strip()
    peso_vendido = st.number_input("🍗 Peso vendido (kg)", min_value=0.0, step=0.01)
    submitted = st.form_submit_button("➕ Agregar venta")
    if submitted:
        if not cliente or peso_vendido <= 0:
            st.warning("Ingresa un cliente válido y un peso mayor a 0.")
        else:
            nueva = pd.DataFrame({"Cliente": [cliente], "Peso vendido (kg)": [peso_vendido]})
            st.session_state.df = pd.concat([st.session_state.df, nueva], ignore_index=True)
            st.success(f"Venta agregada: {cliente} - {peso_vendido:.2f} kg")

# ---------- Tabla + eliminar ----------
st.subheader("📊 Ventas registradas")
st.dataframe(st.session_state.df, use_container_width=True)

st.subheader("🗑️ Eliminar registro")
if not st.session_state.df.empty:
    opciones = st.session_state.df.index.astype(str) + " - " + st.session_state.df["Cliente"]
    seleccion = st.selectbox("Selecciona la venta a eliminar", opciones)
    if st.button("Eliminar"):
        idx = int(seleccion.split(" - ")[0])
        st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
        st.success("Registro eliminado.")

# ---------- Devolución ----------
st.subheader("📦 Devolución")
st.session_state.peso_devolucion = st.number_input(
    "Peso devuelto (kg)", min_value=0.0, step=0.01, value=st.session_state.peso_devolucion
)

# ---------- Cálculos ----------
total_vendido = st.session_state.df["Peso vendido (kg)"].sum()
merma = st.session_state.peso_inicial - (total_vendido + st.session_state.peso_devolucion)
porc_merma = (merma / st.session_state.peso_inicial * 100) if st.session_state.peso_inicial > 0 else 0.0

# ---------- Resumen ----------
st.subheader("📋 Resumen")
st.write(f"⚖️ Peso inicial: **{st.session_state.peso_inicial:.2f} kg**")
st.write(f"🍗 Total vendido: **{total_vendido:.2f} kg**")
st.write(f"📦 Devolución: **{st.session_state.peso_devolucion:.2f} kg**")
st.write(f"📉 Merma: **{merma:.2f} kg** ({porc_merma:.2f}%)")

if st.session_state.peso_inicial > 0:
    if porc_merma <= 2:
        st.success("✅ La merma está dentro del rango permitido (≤ 2%).")
    else:
        st.error("⚠️ La merma supera el 2% permitido.")
else:
    st.info("Ingresa el peso inicial para evaluar el % de merma.")

# ---------- Exportar (Excel + CSV de respaldo) ----------
st.subheader("💾 Exportar datos")
# CSV (siempre disponible)
csv_bytes = st.session_state.df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Descargar CSV (ventas)", data=csv_bytes, file_name="ventas.csv", mime="text/csv")

# Excel (requiere openpyxl)
try:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state.df.to_excel(writer, index=False, sheet_name="Ventas")
        resumen = pd.DataFrame({
            "Peso inicial (kg)": [st.session_state.peso_inicial],
            "Total vendido (kg)": [total_vendido],
            "Devolución (kg)": [st.session_state.peso_devolucion],
            "Merma (kg)": [merma],
            "% Merma": [porc_merma],
        })
        resumen.to_excel(writer, index=False, sheet_name="Resumen")
    st.download_button(
        label="📥 Descargar Excel (ventas + resumen)",
        data=output.getvalue(),
        file_name="control_merma.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
except Exception as e:
    st.info("Para descargar en Excel, asegúrate de tener **openpyxl** en requirements.txt.")

# ---------- Reiniciar ----------
if st.button("🔄 Reiniciar todo"):
    st.session_state.df = pd.DataFrame(columns=["Cliente", "Peso vendido (kg)"])
    st.session_state.peso_inicial = 0.0
    st.session_state.peso_devolucion = 0.0
    st.success("Se reinició el registro.")
    st.rerun()
