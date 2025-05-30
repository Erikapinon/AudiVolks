# Streamlit App: Registro de Entregas para Audivolks Multimarcas

import streamlit as st
import pandas as pd
import datetime
import os

# Inicializar base de datos si no existe
DB_FILE = "base_entregas.csv"
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Usuario", "Cliente", "Ticket", "Monto", "Hora de Salida", "Hora de Llegada"])
    df_init.to_csv(DB_FILE, index=False)

# Cargar base existente
df = pd.read_csv(DB_FILE)

# --- INTERFAZ ---
st.set_page_config(page_title="Registro de Entregas - Audivolks", page_icon="🚗")
st.image("logo.jpg", width=250)

st.title("Registro de Entregas")
usuario = st.selectbox("Selecciona tu usuario", ["ISRA", "SAID", "GABO"])
modo = st.radio("¿Qué deseas hacer?", ["Registrar entrega", "Ver mis entregas"])

if modo == "Registrar entrega":
    st.subheader("Nueva Entrega Múltiple")

    clientes = []
    tickets = []
    montos = []

    for i in range(5):
        st.markdown(f"### Entrega {i+1}")
        cliente = st.text_input(f"Cliente / Destino {i+1}", key=f"cliente_{i}")
        ticket = st.text_input(f"Número de ticket {i+1}", key=f"ticket_{i}")
        monto = st.number_input(f"Monto total {i+1}", min_value=0.0, format="%.2f", key=f"monto_{i}")
        clientes.append(cliente)
        tickets.append(ticket)
        montos.append(monto)

    if st.button("Iniciar entrega"):
        st.session_state["salida"] = datetime.datetime.now()
        st.success(f"Entrega iniciada a las {st.session_state['salida'].strftime('%H:%M:%S')}")

    if st.button("Finalizar entrega"):
        llegada = datetime.datetime.now()
        salida = st.session_state.get("salida", llegada)
        filas = []
        for i in range(5):
            if clientes[i] and tickets[i] and montos[i] > 0:
                fila = {
                    "Usuario": usuario,
                    "Cliente": clientes[i],
                    "Ticket": tickets[i],
                    "Monto": montos[i],
                    "Hora de Salida": salida.strftime("%Y-%m-%d %H:%M:%S"),
                    "Hora de Llegada": llegada.strftime("%Y-%m-%d %H:%M:%S")
                }
                filas.append(fila)
        if filas:
            df_nuevo = pd.DataFrame(filas)
            df_nuevo.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success("Entregas registradas correctamente ✅")
        else:
            st.warning("No hay entregas válidas para registrar.")

elif modo == "Ver mis entregas":
    st.subheader(f"Entregas de {usuario}")
    entregas = df[df["Usuario"] == usuario]
    st.dataframe(entregas)

    if not entregas.empty:
        total = entregas["Monto"].sum()
        st.info(f"Monto total entregado: ${total:,.2f}")
