# Streamlit App: Registro de Entregas para Audivolks Multimarcas - con Admin y botón de impresión

import streamlit as st
import pandas as pd
import datetime
import os

DB_FILE = "base_entregas.csv"
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Usuario", "Cliente", "Ticket", "Monto", "Hora de Salida", "Hora de Llegada"])
    df_init.to_csv(DB_FILE, index=False)

df = pd.read_csv(DB_FILE)

st.set_page_config(page_title="Registro de Entregas - Audivolks", page_icon="🚗")
st.image("logo.jpg", width=250)

st.title("Registro de Entregas")
modo = st.radio("Selecciona el modo", ["Registrar entrega", "Ver mis entregas", "Modo administradora"])

if modo == "Registrar entrega":
    usuario = st.selectbox("Selecciona tu usuario", ["ISRA", "SAID", "GABO"])
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
    usuario = st.selectbox("Selecciona tu usuario", ["ISRA", "SAID", "GABO"])
    st.subheader(f"Entregas de {usuario}")
    entregas = df[df["Usuario"] == usuario]
    st.dataframe(entregas)

    if not entregas.empty:
        total = entregas["Monto"].sum()
        st.info(f"Monto total entregado: ${total:,.2f}")

elif modo == "Modo administradora":
    clave = st.text_input("Introduce tu clave de acceso:", type="password")
    if clave == "admin123":
        st.success("Acceso concedido ✅")
        st.subheader("📊 Reporte General de Entregas")

        if df.empty:
            st.warning("No hay entregas registradas todavía.")
        else:
            st.write("### Total de entregas:", len(df))
            st.write("### Monto total entregado: ${:,.2f}".format(df['Monto'].sum()))

            st.write("### Entregas por repartidor")
            conteo = df["Usuario"].value_counts()
            st.bar_chart(conteo)

            st.write("### Clientes más frecuentes")
            clientes = df["Cliente"].value_counts().head(10)
            st.bar_chart(clientes)

            df["Hora de Salida"] = pd.to_datetime(df["Hora de Salida"])
            df["Hora de Llegada"] = pd.to_datetime(df["Hora de Llegada"])
            df["Duración (min)"] = (df["Hora de Llegada"] - df["Hora de Salida"]).dt.total_seconds() / 60

            if not df["Duración (min)"].isnull().all():
                st.write("### Tiempo promedio por entrega")
                tiempo_prom = df["Duración (min)"].mean()
                st.metric("Tiempo promedio (min)", f"{tiempo_prom:.2f}")
            else:
                st.info("Aún no hay datos suficientes de tiempo.")

            st.markdown("---")
            st.markdown("### 🖨️ Imprimir Reporte")
            st.markdown("Presiona **Ctrl + P** (o usa el botón de imprimir del navegador) para guardar este reporte como PDF o imprimirlo.")
    else:
        if clave:
            st.error("Clave incorrecta ❌")
Actualización con vista administradora
