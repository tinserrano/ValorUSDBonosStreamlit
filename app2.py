
import streamlit as st
from utils.api_functions import obtener_access_token

def main():
    st.set_page_config(page_title="Análisis de Bonos", layout="wide")
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title('Iniciar Sesión')
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

    if st.button('Iniciar Sesión'):
        if username and password:
            access_token, error = obtener_access_token(username, password)
            if access_token:
                st.session_state.access_token = access_token
                st.session_state.authenticated = True
                st.success("Sesión iniciada con éxito")
                st.experimental_rerun()
            else:
                st.error(f"No se pudo iniciar sesión. Error: {error}")
        else:
            st.warning("Por favor, ingresa tu usuario y contraseña")
    else:
        st.sidebar.title("Navegación")
        st.sidebar.page_link("app2.py", label="Inicio")
        st.sidebar.page_link("pages/cotizaciones.py", label="Cotizaciones")
        st.sidebar.page_link("pages/tipo_de_cambio.py", label="Tipo de Cambio")
        
        if st.sidebar.button('Cerrar Sesión'):
            st.session_state.authenticated = False
            st.session_state.pop('access_token', None)
            st.experimental_rerun()
        
        st.title('Bienvenido al Análisis de Bonos')
        st.write('Selecciona una opción del menú lateral para comenzar.')

if __name__ == "__main__":
    main()