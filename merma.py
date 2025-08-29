import streamlit as st
import pandas as pd

st.title("📊 Cálculo de Merma - Venta de Pollo Entero")

# Entrada del peso inicial
peso_inicial = st.number_input("Ingrese el peso inicial (kg):", min_value=0.0, format="%.2f")

# Lista de ventas
st.subheader("Ventas realizadas")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Cliente", "Peso (kg)"])

# Formulario para agregar ventas
with st.form("form_venta"):
    cliente = st.text_input("Nombre del cliente")
    peso = st.number_input("Peso vendido (kg)", min_value=0.0, format="%.2f")
    submit = st.form_submit_button("Agregar venta")

    if submit and cliente and peso > 0:
        nueva_venta = pd.DataFrame({"Cliente": [cliente], "Peso (kg)": [peso]})
        st.session_state.df = pd.concat([st.session_state.df, nueva_venta], ignore_index=True)

# Mostrar tabla de ventas
st.dataframe(st.session_state.df)

# Entrada devolución
devolucion = st.number_input("Ingrese el peso devuelto (kg):", min_value=0.0, format="%.2f")

# Botón calcular
if st.button("Calcular Merma"):
    peso_vendido = st.session_state.df["Peso (kg)"].sum()
    merma = peso_inicial - (peso_vendido + devolucion)
    porcentaje_merma = (merma / peso_inicial) * 100 if peso_inicial > 0 else 0

    st.subheader("📋 Resultados")
    st.write(f"**Peso inicial:** {peso_inicial:.2f} kg")
    st.write(f"**Peso vendido:** {peso_vendido:.2f} kg")
    st.write(f"**Devolución:** {devolucion:.2f} kg")
    st.write(f"**Merma:** {merma:.2f} kg (**{porcentaje_merma:.2f}%**)")

    if porcentaje_merma <= 2:
        st.success("✅ Merma dentro del rango permitido (≤ 2%)")
    else:
        st.error("⚠️ Atención: Merma superior al 2%")
