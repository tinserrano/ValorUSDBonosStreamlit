import streamlit as st
from utils.api_functions import obtener_access_token
from footer import footer
import os


def setup_sidebar():
    st.sidebar.title("Navegación")
    
    # Enlace a la página principal
    if st.sidebar.button("Inicio"):
        st.switch_page("app2.py")
    
    # Enlace a la página de Cotizaciones
    if st.sidebar.button("Cotizaciones"):
        if os.path.exists("pages/Cotizaciones.py"):
            st.switch_page("pages/Cotizaciones.py")
        elif os.path.exists("pages/cotizaciones.py"):
            st.switch_page("pages/cotizaciones.py")
        else:
            st.sidebar.error("Página de Cotizaciones no encontrada")
    
    # Enlace a la página de Tipo de Cambio
    if st.sidebar.button("Tipo de Cambio"):
        if os.path.exists("pages/tipo_de_cambio.py"):
            st.switch_page("pages/tipo_de_cambio.py")
        else:
            st.sidebar.error("Página de Tipo de Cambio no encontrada")
    
    if st.sidebar.button('Cerrar Sesión'):
        st.session_state.authenticated = False
        st.session_state.pop('access_token', None)
        st.rerun()

def login_form():
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
                st.rerun()
            else:
                st.error(f"No se pudo iniciar sesión. Error: {error}")
        else:
            st.warning("Por favor, ingresa tu usuario y contraseña")
    
    st.markdown("---")
    st.write("Los datos a ingresar corresponden a la API de Invertir Online")
    



def main():
    st.set_page_config(page_title="Análisis de Bonos", layout="wide")
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        setup_sidebar()
        st.title('Bienvenido al Análisis de Bonos')
        st.write('Selecciona una opción del menú lateral para comenzar.')
    else:
        login_form()
    
    

if __name__ == "__main__":
    main()
    footer()