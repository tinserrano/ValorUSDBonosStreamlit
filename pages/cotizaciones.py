import streamlit as st
from utils.api_functions import obtener_y_procesar_datos




def show():
    st.title('Cotizaciones de Bonos')
    
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning('Por favor, inicia sesión primero.')
        return

    if st.button('Actualizar Cotizaciones'):
        with st.spinner('Obteniendo datos de cotizaciones...'):
            df_bonos = obtener_y_procesar_datos(st.session_state.access_token)
        
        if not df_bonos.empty:
            st.dataframe(df_bonos)
        else:
            st.error("No se pudieron obtener datos de cotizaciones")

if __name__ == "__main__":
    show()