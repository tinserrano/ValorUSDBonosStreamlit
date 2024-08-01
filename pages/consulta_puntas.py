import streamlit as st
from utils.api_functions import obtener_cotizacion_detalle_v2
import pandas as pd
from dateutil import parser
from footer import footer


def format_fecha_hora(fecha_hora_str):
    try:
        fecha_hora = parser.isoparse(fecha_hora_str)
        return fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return fecha_hora_str

def show():
    st.title('Consulta de Puntas y Datos de Cotización')
    
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning('Por favor, inicia sesión primero.')
        return

    ticker = st.text_input("Ingrese el ticker/especie a consultar")

    if st.button('Consultar Datos'):
        if not ticker:
            st.error("Por favor, ingrese un ticker/especie para consultar.")
        else:
            with st.spinner('Obteniendo datos de cotización...'):
                cotizacion, error = obtener_cotizacion_detalle_v2(st.session_state.access_token, "bCBA", ticker)
            
            if error:
                st.error(f"Error al obtener la cotización: {error}")
            elif cotizacion:
                st.success(f"Datos obtenidos con éxito para {ticker}")
                

                st.subheader(f"Datos Generales de Cotización de {ticker}")
                st.write(f"Fecha y Hora: {format_fecha_hora(cotizacion.get('fechaHora', ''))}")
                tendencia = cotizacion.get('tendencia', '').lower()
                tendencia_emoji = "⬆️" if tendencia == "sube" else "⬇️" if tendencia == "baja" else "➡️"
                variacion = cotizacion.get('variacion', 0)
                variacion_color = "green" if variacion > 0 else "red" if variacion < 0 else "black"
                st.markdown(f"<span style='color:{variacion_color}'>Variación: {variacion}%</span>", unsafe_allow_html=True)
                
                st.write(f"Tendencia: {tendencia.capitalize()} {tendencia_emoji}")

                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Último Precio", cotizacion.get('ultimoPrecio', 0))
                    st.metric("Apertura", cotizacion.get('apertura', 0))
                
                with col2:
                    
                    st.metric("Mínimo", cotizacion.get('minimo', 0))
                    st.metric("Cierre Anterior", cotizacion.get('cierreAnterior', 0))
                
                with col3:
                    st.metric("Monto Operado", cotizacion.get('montoOperado', 0))
                    st.metric("Máximo", cotizacion.get('maximo', 0))
                    st.metric("Volumen Nominal", cotizacion.get('volumenNominal', 0))

                
                

                

                
                puntas = cotizacion.get('puntas', [])
                if puntas:
                    st.subheader("Puntas de Compra/Venta")
                    
                    compras = []
                    ventas = []
                    for punta in puntas:
                        if punta.get('precioCompra'):
                            compras.append({
                                'Precio': punta['precioCompra'],
                                'Cantidad': punta['cantidadCompra']
                            })
                        if punta.get('precioVenta'):
                            ventas.append({
                                'Precio': punta['precioVenta'],
                                'Cantidad': punta['cantidadVenta']
                            })
                    
                    compras_df = pd.DataFrame(compras).sort_values('Precio', ascending=False)
                    ventas_df = pd.DataFrame(ventas).sort_values('Precio')
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Ofertas de Compra")
                        st.dataframe(compras_df)
                    
                    with col2:
                        st.subheader("Ofertas de Venta")
                        st.dataframe(ventas_df)
                    
                else:
                    st.warning("No se encontraron puntas para este ticker.")
            else:
                st.error(f"No se pudo obtener la cotización para {ticker}")

if __name__ == "__main__":
    show()
    footer()