import streamlit as st
from utils.api_functions import obtener_cotizacion_detalle_v2

def show():
    st.title('Consulta de Puntas')
    
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning('Por favor, inicia sesión primero.')
        return

    # Campo para el ticker
    ticker = st.text_input("Ingrese el ticker/especie a consultar")

    # Botón para realizar la consulta
    if st.button('Consultar Puntas'):
        if not ticker:
            st.error("Por favor, ingrese un ticker/especie para consultar.")
        else:
            with st.spinner('Obteniendo datos de cotización...'):
                cotizacion, error = obtener_cotizacion_detalle_v2(st.session_state.access_token, "bCBA", ticker)
            
            if error:
                st.error(f"Error al obtener la cotización: {error}")
            elif cotizacion:
                st.success(f"Cotización detalle obtenida con éxito para {ticker}")
                
                # Extraer y mostrar las puntas
                puntas = cotizacion.get('puntas', [])
                if puntas:
                    st.subheader("Puntas de Compra/Venta")
                    for i, punta in enumerate(puntas, 1):
                        st.write(f"Punta {i}:")
                        st.write(f"Precio Compra: {punta.get('precioCompra')}")
                        st.write(f"Precio Venta: {punta.get('precioVenta')}")
                        st.write(f"Cantidad Compra: {punta.get('cantidadCompra')}")
                        st.write(f"Cantidad Venta: {punta.get('cantidadVenta')}")
                        st.write("---")
                else:
                    st.warning("No se encontraron puntas para este ticker.")
            else:
                st.error(f"No se pudo obtener la cotización para {ticker}")

if __name__ == "__main__":
    show()