# Streamlit App: Registro de Entregas para Audivolks Multimarcas

import streamlit as st
import pandas as pd
import datetime
import os
import pytz
from io import BytesIO

# Zona horaria CST
cst = pytz.timezone("America/Mexico_City")

# Inicializar base de datos si no existe
DB_FILE = "base_entregas.csv"
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Usuario", "Cliente", "Ticket", "Monto", "Hora de Salida", "Hora de Llegada"])
    df_init.to_csv(DB_FILE, index=False)

# Cargar base existente
@st.cache_data(ttl=60)
def cargar_datos():
    df_local = pd.read_csv(DB_FILE)
    df_local["Hora de Salida"] = pd.to_datetime(df_local["Hora de Salida"])
    df_local["Hora de Llegada"] = pd.to_datetime(df_local["Hora de Llegada"])
    return df_local

df = cargar_datos()

# --- INTERFAZ ---
st.set_page_config(page_title="Registro de Entregas - Audivolks", page_icon="🚗")
st.image("logo.jpg", width=250)

st.title("Registro de Entregas")
usuario = st.selectbox("Selecciona tu usuario", ["ISRA", "SAID", "GABO", "ALEX"])
modo = st.radio("¿Qué deseas hacer?", ["Registrar entrega", "Ver mis entregas", "Modo administradora"])

if modo == "Registrar entrega":
    st.subheader("Nueva(s) Entrega(s)")
    num_entregas = st.slider("¿Cuántas entregas quieres registrar?", 1, 5, 1)

    for i in range(num_entregas):
        st.markdown(f"### Entrega {i+1}")
        cliente = st.text_input(f"Cliente / Destino {i+1}", key=f"cliente_{i}")
        ticket = st.text_input(f"Número de ticket {i+1}", key=f"ticket_{i}")
        monto = st.number_input(f"Monto total {i+1}", min_value=0.0, format="%.2f", key=f"monto_{i}")

        if st.button(f"Iniciar entrega {i+1}", key=f"inicio_{i}"):
            salida = datetime.datetime.now(cst)
            st.session_state[f"salida_{i}"] = salida
            st.success(f"Entrega {i+1} iniciada a las {salida.strftime('%H:%M:%S')}")

        if st.button(f"Finalizar entrega {i+1}", key=f"fin_{i}"):
            llegada = datetime.datetime.now(cst)
            salida = st.session_state.get(f"salida_{i}", llegada)
            nueva_fila = pd.DataFrame({
                "Usuario": [usuario],
                "Cliente": [cliente],
                "Ticket": [ticket],
                "Monto": [monto],
                "Hora de Salida": [salida.strftime("%Y-%m-%d %H:%M:%S")],
                "Hora de Llegada": [llegada.strftime("%Y-%m-%d %H:%M:%S")]
            })
            nueva_fila.to_csv(DB_FILE, mode='a', header=False, index=False)
            st.success(f"Entrega {i+1} registrada correctamente ✅")
            st.cache_data.clear()
            st.experimental_rerun()

elif modo == "Ver mis entregas":
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

            # --- Reporte Diario ---
            st.markdown("---")
            st.subheader("🗓️ Reporte Diario")
            fecha_seleccionada = st.date_input("Selecciona una fecha", datetime.date.today())

            df["Fecha"] = df["Hora de Salida"].dt.date
            entregas_dia = df[df["Fecha"] == fecha_seleccionada]

            if entregas_dia.empty:
                st.warning("No hay entregas registradas en esa fecha.")
            else:
                resumen = entregas_dia.groupby("Usuario")["Monto"].agg(["count", "sum"]).rename(columns={"count": "Entregas", "sum": "Monto Total"})
                st.dataframe(resumen)

                for usuario in resumen.index:
                    st.info(f"{usuario}: {resumen.loc[usuario, 'Entregas']} entregas - ${resumen.loc[usuario, 'Monto Total']:.2f}")

                # Descargar como Excel
                buffer_excel = BytesIO()
                entregas_dia.to_excel(buffer_excel, index=False, engine='openpyxl')
                st.download_button("📥 Descargar reporte diario en Excel", data=buffer_excel.getvalue(), file_name=f"reporte_diario_{fecha_seleccionada}.xlsx")

                # Descargar como CSV
                csv_buffer = entregas_dia.to_csv(index=False).encode()
                st.download_button("📥 Descargar reporte diario en CSV", data=csv_buffer, file_name=f"reporte_diario_{fecha_seleccionada}.csv")

            # --- Reporte Semanal y Mensual ---
            st.subheader("🔁 Reporte Semanal y Mensual")
            hoy = datetime.date.today()
            semana_actual = df[df["Fecha"] >= hoy - datetime.timedelta(days=7)]
            mes_actual = df[df["Fecha"] >= hoy.replace(day=1)]

            if not semana_actual.empty:
                st.write("### Reporte Semanal")
                resumen_semana = semana_actual.groupby("Usuario")["Monto"].agg(["count", "sum"]).rename(columns={"count": "Entregas", "sum": "Monto Total"})
                st.dataframe(resumen_semana)
                buffer_excel = BytesIO()
                semana_actual.to_excel(buffer_excel, index=False, engine='openpyxl')
                st.download_button("📥 Descargar reporte semanal (Excel)", data=buffer_excel.getvalue(), file_name="reporte_semanal.xlsx")

            if not mes_actual.empty:
                st.write("### Reporte Mensual")
                resumen_mes = mes_actual.groupby("Usuario")["Monto"].agg(["count", "sum"]).rename(columns={"count": "Entregas", "sum": "Monto Total"})
                st.dataframe(resumen_mes)
                buffer_excel = BytesIO()
                mes_actual.to_excel(buffer_excel, index=False, engine='openpyxl')
                st.download_button("📥 Descargar reporte mensual (Excel)", data=buffer_excel.getvalue(), file_name="reporte_mensual.xlsx")
    else:
        if clave:
            st.error("Clave incorrecta ❌")
