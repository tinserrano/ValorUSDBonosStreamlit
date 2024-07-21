import streamlit as st
from supabase import create_client, Client
import pandas as pd
import locale
from datetime import datetime
from dotenv import load_dotenv
import os

# Configura tu URL y clave API de Supabase
#SUPABASE_URL = os.getenv('SUPABASE_URL')
#SUPABASE_KEY = os.getenv('SUPABASE_KEY')


SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_API_KEY = st.secrets["SUPABASE_API_KEY"]



SUPABASE_TABLE = "data"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_API_KEY)

@st.cache_data
def load_data():
    supabase = init_supabase()
    response = supabase.table("data").select("*").execute()
    data = response.data
    return pd.DataFrame(data)

def formato_numero(numero):
    return locale.format_string('%.2f', numero, grouping=True).replace('.', ',')

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
    st.title("Cálculo de Tipo de Cambio Implícito")

    st.write("Cargando datos desde Supabase...")
    df_bonos = load_data()

    st.write("Datos cargados. Calculando tipo de cambio implícito...")
    df_tipo_cambio = calcular_tipo_cambio_implicito(df_bonos)

    st.write("Cálculo completado!")

    # Filtros dinámicos
    plazos_ars = df_tipo_cambio['Plazo ARS'].unique()
    plazos_ars_seleccionados = st.multiselect("Selecciona los plazos ARS a mostrar:", options=plazos_ars, default=plazos_ars)

    plazos_usd = df_tipo_cambio['Plazo USD'].unique()
    plazos_usd_seleccionados = st.multiselect("Selecciona los plazos USD a mostrar:", options=plazos_usd, default=plazos_usd)

    # Filtrar DataFrame según las selecciones del usuario
    df_filtrado = df_tipo_cambio[
        df_tipo_cambio['Plazo ARS'].isin(plazos_ars_seleccionados) &
        df_tipo_cambio['Plazo USD'].isin(plazos_usd_seleccionados)
    ]

    st.dataframe(df_filtrado)

if __name__ == "__main__":
    main()