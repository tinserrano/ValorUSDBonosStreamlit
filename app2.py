#se puede consumir directamente desde Streamlit a API?



import locale
import pandas as pd
from datetime import datetime
import streamlit as st
import requests
from contras import usernw, passw2
from dateutil import parser
import concurrent.futures

# Configurar la localización para usar coma como separador decimal
locale.setlocale(locale.LC_NUMERIC, 'es_ES.UTF-8')

def parse_fecha_hora(fecha_hora_str):
    try:
        return parser.isoparse(fecha_hora_str)
    except ValueError:
        try:
            fecha_hora_limpia = fecha_hora_str.split('.')[0]
            offset = fecha_hora_str.split('-')[-1]
            fecha_hora_limpia += f"-{offset}"
            return parser.isoparse(fecha_hora_limpia)
        except Exception as e:
            st.error(f"No se pudo parsear la fecha: {fecha_hora_str}")
            st.error(f"Error: {e}")
            return None

def formato_numero(numero):
    return locale.format_string('%.2f', numero, grouping=True).replace('.', ',')

def obtener_access_token():
    url = "https://api.invertironline.com/token"
    username = usernw()
    password = passw2()

    data = {
        "username": username,
        "password": password,
        "grant_type": "password"
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data['access_token']
        st.success("Token obtenido con éxito!")
        return access_token
    except requests.RequestException as e:
        st.error(f"Error al obtener el token: {e}")
        return None

def obtener_cotizacion_detalle(access_token, mercado, bono, plazo):
    base_url = "https://api.invertironline.com"
    endpoint = f"/api/v2/{mercado}/Titulos/{bono}/CotizacionDetalleMobile/{plazo}"
    url = base_url + endpoint
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        cotizacion = response.json()
        st.success(f"Cotización obtenida con éxito para {bono} {plazo}")
        return cotizacion
    except requests.RequestException as e:
        st.error(f"Error al obtener la cotización para {bono} {plazo}: {e}")
        st.error(f"Respuesta: {e.response.text if e.response else 'No response'}")
        return None
def obtener_datos_bono(access_token, mercado, bono, plazos):
    datos_bono = []
    for plazo in plazos:
        cotizacion = obtener_cotizacion_detalle(access_token, mercado, bono, plazo)
        if cotizacion:
            puntas = cotizacion.get('puntas', [])
            mejor_punta = puntas[0] if puntas else {}

            row_dict = {
                'Bono': bono,
                'Plazo': plazo,
                'Último Precio': cotizacion.get('ultimoPrecio'),
                'Variación': cotizacion.get('variacion'),
                'Apertura': cotizacion.get('apertura'),
                'Máximo': cotizacion.get('maximo'),
                'Mínimo': cotizacion.get('minimo'),
                'Fecha Hora': parse_fecha_hora(cotizacion.get('fechaHora', '')) if cotizacion.get('fechaHora') else None,
                'Monto Operado': cotizacion.get('montoOperado'),
                'Mejor Punta Compra Precio': mejor_punta.get('precioCompra'),
                'Mejor Punta Venta Precio': mejor_punta.get('precioVenta')
            }
            datos_bono.append(row_dict)
        else:
            st.warning(f"No se pudieron obtener datos para {bono} {plazo}")
    return datos_bono

def obtener_y_procesar_datos():
    bonos = ['AL30', 'GD30', 'AL29', 'GD29', 'AL30D', 'GD30D', 'AL29D', 'GD29D', 'AE38', 'AE38D', 'GD38', 'GD38D', 'GD41', 'GD41D', 'GD46', 'GD46D', 'AL35', 'AL35D', 'AL41', 'AL41D', 'GD35', 'GD35D']
    plazos = ['t0', 't1']
    mercado = 'bCBA'

    access_token = obtener_access_token()
    if not access_token:
        st.error("No se pudo obtener el token. Abortando la operación")
        return pd.DataFrame()

    datos = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(obtener_datos_bono, access_token, mercado, bono, plazos) for bono in bonos]
        for future in concurrent.futures.as_completed(futures):
            datos.extend(future.result())

    return pd.DataFrame(datos)

def calcular_tipo_cambio_implicito(df):
    # Lista de todos los bonos
    bonos = ['AL29', 'AL30', 'AL35', 'AE38', 'AL41', 'GD29', 'GD30', 'GD35', 'GD38', 'GD41', 'GD46']
    
    bonos_pares = [(bono, bono + 'D') for bono in bonos]
    combinaciones_plazos = [('t0', 't0'), ('t0', 't1'), ('t1', 't1')]
    
    resultados = []

    for bono_peso, bono_dolar in bonos_pares:
        for plazo_peso, plazo_dolar in combinaciones_plazos:
            # Datos para el último precio
            ultimo_precio_peso = df[(df['Bono'] == bono_peso) & (df['Plazo'] == plazo_peso)]['Último Precio'].values
            ultimo_precio_dolar = df[(df['Bono'] == bono_dolar) & (df['Plazo'] == plazo_dolar)]['Último Precio'].values
            
            # Datos para COMPRAUSD
            precio_venta_peso_compra = df[(df['Bono'] == bono_peso) & (df['Plazo'] == plazo_peso)]['Mejor Punta Venta Precio'].values
            precio_compra_dolar_compra = df[(df['Bono'] == bono_dolar) & (df['Plazo'] == plazo_dolar)]['Mejor Punta Compra Precio'].values
            
            # Datos para VENTAUSD
            precio_compra_peso_venta = df[(df['Bono'] == bono_peso) & (df['Plazo'] == plazo_peso)]['Mejor Punta Compra Precio'].values
            precio_venta_dolar_venta = df[(df['Bono'] == bono_dolar) & (df['Plazo'] == plazo_dolar)]['Mejor Punta Venta Precio'].values
            
            if (len(ultimo_precio_peso) > 0 and len(ultimo_precio_dolar) > 0 and ultimo_precio_dolar[0] != 0 and
                len(precio_venta_peso_compra) > 0 and len(precio_compra_dolar_compra) > 0 and precio_compra_dolar_compra[0] != 0 and
                len(precio_compra_peso_venta) > 0 and len(precio_venta_dolar_venta) > 0 and precio_venta_dolar_venta[0] != 0):
                
                tipo_cambio_ultimo = ultimo_precio_peso[0] / ultimo_precio_dolar[0]
                tipo_cambio_compra_usd = precio_venta_peso_compra[0] / precio_compra_dolar_compra[0]
                tipo_cambio_venta_usd = precio_compra_peso_venta[0] / precio_venta_dolar_venta[0]
                
                resultados.append({
                    'Bono': f'{bono_peso}/{bono_dolar}',
                    'Plazo ARS': plazo_peso,
                    'Plazo USD': plazo_dolar,
                    'Último Precio ARS': formato_numero(ultimo_precio_peso[0]),
                    'Último Precio USD': formato_numero(ultimo_precio_dolar[0]),
                    'Tipo de Cambio Implícito (Último)': formato_numero(tipo_cambio_ultimo),
                    'Precio Venta ARS (COMPRAUSD)': formato_numero(precio_venta_peso_compra[0]),
                    'Precio Compra USD (COMPRAUSD)': formato_numero(precio_compra_dolar_compra[0]),
                    'Tipo de Cambio Implícito (COMPRAUSD)': formato_numero(tipo_cambio_compra_usd),
                    'Precio Compra ARS (VENTAUSD)': formato_numero(precio_compra_peso_venta[0]),
                    'Precio Venta USD (VENTAUSD)': formato_numero(precio_venta_dolar_venta[0]),
                    'Tipo de Cambio Implícito (VENTAUSD)': formato_numero(tipo_cambio_venta_usd),
                    'fecha_hora_consulta': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                })
            else:
                st.warning(f"No se pudo calcular el tipo de cambio para {bono_peso}({plazo_peso})/{bono_dolar}({plazo_dolar})")

    return pd.DataFrame(resultados)

def main():
    st.title('Cotizaciones de Bonos y Tipo de Cambio Implícito')

    if st.button('Actualizar Datos'):
        with st.spinner('Obteniendo datos de cotizaciones...'):
            df_bonos = obtener_y_procesar_datos()
        
        if not df_bonos.empty:
            st.subheader('Cotizaciones de Bonos')
            st.dataframe(df_bonos)

            with st.spinner('Calculando tipo de cambio implícito...'):
                df_tipo_cambio = calcular_tipo_cambio_implicito(df_bonos)
            
            if not df_tipo_cambio.empty:
                st.subheader('Tipo de Cambio Implícito')
                st.dataframe(df_tipo_cambio)
            else:
                st.error("No se pudo calcular el tipo de cambio implícito")
        else:
            st.error("No se pudieron obtener datos de cotizaciones")

if __name__ == "__main__":
    main()