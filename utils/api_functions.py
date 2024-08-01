import streamlit as st
import requests
import pandas as pd
import concurrent.futures
from config import API_BASE_URL
from dateutil import parser



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
    


def obtener_access_token(username, password):
    url = f"{API_BASE_URL}/token"
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
        return access_token, None  # Retorna el token y None como error
    except requests.RequestException as e:
        return None, str(e)  # Retorna None como token y el error como string

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
    
def obtener_cotizacion_detalle_v2(access_token, mercado, simbolo):
    base_url = "https://api.invertironline.com"
    endpoint = f"/api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalle"
    url = base_url + endpoint
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        cotizacion = response.json()
        st.success(f"Cotización detalle obtenida con éxito para {simbolo}")
        return cotizacion
    except requests.RequestException as e:
        st.error(f"Error al obtener la cotización detalle para {simbolo}: {e}")
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


def obtener_cotizacion_detalle_v2(access_token, mercado, simbolo):
    base_url = "https://api.invertironline.com"
    endpoint = f"/api/v2/{mercado}/Titulos/{simbolo}/CotizacionDetalle"
    url = base_url + endpoint
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        cotizacion = response.json()
        return cotizacion, None
    except requests.RequestException as e:
        return None, str(e)



def obtener_y_procesar_datos(access_token):
    bonos = ['AL30', 'GD30', 'AL29', 'GD29', 'AL30D', 'GD30D', 'AL29D', 'GD29D', 'AE38', 'AE38D', 'GD38', 'GD38D', 'GD41', 'GD41D', 'GD46', 'GD46D', 'AL35', 'AL35D', 'AL41', 'AL41D', 'GD35', 'GD35D']
    plazos = ['t0', 't1']
    mercado = 'bCBA'

    datos = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(obtener_datos_bono, access_token, mercado, bono, plazos) for bono in bonos]
        for future in concurrent.futures.as_completed(futures):
            datos.extend(future.result())

    return pd.DataFrame(datos)