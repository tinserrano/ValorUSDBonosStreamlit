def obtener_cotizacion_puntas(access_token, mercado, simbolo):
    base_url = "https://api.invertironline.com"
    endpoint = f"/api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalle"
    url = base_url + endpoint

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener datos para {simbolo}. Código de estado: {response.status_code}")
        return None








consulta_instrumento_puntas.py:
import streamlit as st
import pandas as pd
from utils.api_functions import obtener_cotizacion_puntas, obtener_y_procesar_datos

def show():
    st.title('Cotizaciones y Puntas')
    
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning('Por favor, inicia sesión primero.')
        return

    # Sección para mostrar todas las cotizaciones
    if st.button('Actualizar Cotizaciones'):
        with st.spinner('Obteniendo datos de cotizaciones...'):
            df_bonos = obtener_y_procesar_datos(st.session_state.access_token)
        
        if not df_bonos.empty:
            st.dataframe(df_bonos)
        else:
            st.error("No se pudieron obtener datos de cotizaciones")

    # Sección para consultar puntas de un bono específico
    st.subheader('Consulta de Puntas')
    mercado = st.selectbox("Seleccione el mercado", ["bCBA", "NYSE", "NASDAQ"])
    bono = st.text_input("Ingrese el símbolo del bono").upper()

    if st.button('Consultar Puntas'):
        if bono:
            with st.spinner(f'Obteniendo puntas para {bono}...'):
                cotizacion = obtener_cotizacion_puntas(st.session_state.access_token, mercado, bono)
                if cotizacion:
                    st.success(f"Cotización obtenida para {bono}")
                    
                    # Mostrar información general
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Último Precio", cotizacion['ultimoPrecio'])
                    col2.metric("Variación", f"{cotizacion['variacion']}%")
                    col3.metric("Monto Operado", cotizacion['montoOperado'])
                    
                    # Mostrar puntas
                    st.subheader("Puntas")
                    puntas_df = pd.DataFrame(cotizacion['puntas'])
                    st.dataframe(puntas_df)
                else:
                    st.error(f"No se pudo obtener la cotización para {bono}")
        else:
            st.warning("Por favor, ingrese un símbolo de bono")

if __name__ == "__main__":
    show()