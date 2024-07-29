import streamlit as st
from utils.api_functions import obtener_y_procesar_datos
from utils.data_processing import calcular_tipo_cambio_implicito

def show():
    st.title('Tipo de Cambio Implícito')
    
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning('Por favor, inicia sesión primero.')
        return

    if st.button('Calcular Tipo de Cambio Implícito'):
        with st.spinner('Obteniendo datos y calculando...'):
            df_bonos = obtener_y_procesar_datos(st.session_state.access_token)
            df_tipo_cambio = calcular_tipo_cambio_implicito(df_bonos)
        
        if not df_tipo_cambio.empty:
            st.dataframe(df_tipo_cambio)
        else:
            st.error("No se pudo calcular el tipo de cambio implícito")

if __name__ == "__main__":
    show()