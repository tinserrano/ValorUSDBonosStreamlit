import pandas as pd
from datetime import datetime

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
            
            # Verificar que todos los valores necesarios estén presentes y no sean cero
            if (len(ultimo_precio_peso) > 0 and len(ultimo_precio_dolar) > 0 and 
                len(precio_venta_peso_compra) > 0 and len(precio_compra_dolar_compra) > 0 and 
                len(precio_compra_peso_venta) > 0 and len(precio_venta_dolar_venta) > 0):
                
                # Usar el primer valor de cada array y verificar que no sea cero
                up_peso = ultimo_precio_peso[0]
                up_dolar = ultimo_precio_dolar[0]
                pvpc = precio_venta_peso_compra[0]
                pcdc = precio_compra_dolar_compra[0]
                pcpv = precio_compra_peso_venta[0]
                pvdv = precio_venta_dolar_venta[0]
                
                if up_dolar and up_peso and pcdc and pvpc and pvdv and pcpv:
                    tipo_cambio_ultimo = up_peso / up_dolar
                    tipo_cambio_compra_usd = pvpc / pcdc
                    tipo_cambio_venta_usd = pcpv / pvdv
                    
                    resultados.append({
                        'Bono': f'{bono_peso}/{bono_dolar}',
                        'Plazo ARS': plazo_peso,
                        'Plazo USD': plazo_dolar,
                        'Último Precio ARS': formato_numero(up_peso),
                        'Último Precio USD': formato_numero(up_dolar),
                        'Tipo de Cambio Implícito (Último)': formato_numero(tipo_cambio_ultimo),
                        'Precio Venta ARS (COMPRAUSD)': formato_numero(pvpc),
                        'Precio Compra USD (COMPRAUSD)': formato_numero(pcdc),
                        'Tipo de Cambio Implícito (COMPRAUSD)': formato_numero(tipo_cambio_compra_usd),
                        'Precio Compra ARS (VENTAUSD)': formato_numero(pcpv),
                        'Precio Venta USD (VENTAUSD)': formato_numero(pvdv),
                        'Tipo de Cambio Implícito (VENTAUSD)': formato_numero(tipo_cambio_venta_usd),
                        'fecha_hora_consulta': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    })
                else:
                    print(f"Valores cero o nulos encontrados para {bono_peso}({plazo_peso})/{bono_dolar}({plazo_dolar})")
            else:
                print(f"Datos insuficientes para {bono_peso}({plazo_peso})/{bono_dolar}({plazo_dolar})")

    return pd.DataFrame(resultados)


def formato_numero(numero):
    return locale.format_string('%.2f', numero, grouping=True).replace('.', ',')

