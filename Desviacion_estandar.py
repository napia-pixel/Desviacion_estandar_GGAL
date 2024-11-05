import streamlit as st
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import norm
from datetime import date

# [Previous imports and configurations remain the same...]

def graficar_distribucion_normal(simbolo, dias_proyeccion=30, periodo='1y'):
    """
    Crea un gráfico de la distribución normal de posibles precios futuros.
    """
    # Obtener datos y calcular volatilidad
    datos = obtener_datos(simbolo, periodo)
    if datos is None:
        return
    
    volatilidad = calcular_volatilidad(datos)
    
    precio_actual = datos['Close'].iloc[-1]
    volatilidad_actual = volatilidad.iloc[-1]

    # Calcular sigma ajustado por tiempo
    sigma = volatilidad_actual * np.sqrt(dias_proyeccion / 252)
    
    # Crear rango de precios para la distribución
    rango_precios = np.linspace(
        precio_actual * (1 - 3 * sigma),
        precio_actual * (1 + 3 * sigma),
        200
    )

    # Calcular la distribución normal
    distribucion = norm.pdf(rango_precios, precio_actual, precio_actual * sigma)

    # Calcular intervalos de confianza
    conf_68 = norm.interval(0.68, precio_actual, precio_actual * sigma)
    conf_95 = norm.interval(0.95, precio_actual, precio_actual * sigma)
    conf_99 = norm.interval(0.99, precio_actual, precio_actual * sigma)

    # Crear gráfico
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(rango_precios, distribucion, 'b-', lw=2, label='Distribución de precios')
    
    # Agregar áreas sombreadas para los intervalos de confianza
    ax.fill_between(rango_precios, distribucion, 
                    where=(rango_precios >= conf_68[0]) & (rango_precios <= conf_68[1]),
                    color='blue', alpha=0.3, 
                    label=f'68%: ${conf_68[0]:.2f} - ${conf_68[1]:.2f}')
    ax.fill_between(rango_precios, distribucion, 
                    where=(rango_precios >= conf_95[0]) & (rango_precios <= conf_95[1]),
                    color='blue', alpha=0.2, 
                    label=f'95%: ${conf_95[0]:.2f} - ${conf_95[1]:.2f}')
    ax.fill_between(rango_precios, distribucion, 
                    where=(rango_precios >= conf_99[0]) & (rango_precios <= conf_99[1]),
                    color='blue', alpha=0.1, 
                    label=f'99%: ${conf_99[0]:.2f} - ${conf_99[1]:.2f}')

    ax.axvline(precio_actual, color='red', linestyle='--', 
               label=f'Precio actual: ${precio_actual:.2f}')
    
    # Agregar marca de agua
    ax.text(0.02, 0.02, 'by Napia', 
            transform=ax.transAxes,  # Usar coordenadas relativas al eje
            fontsize=10, 
            color='gray', 
            alpha=0.7,
            style='italic')
    
    ax.set_yticklabels([])
    ax.set_title(f'Distribución Normal de Precios Proyectados a {dias_proyeccion} días\n{simbolo}')
    ax.set_xlabel('Precio')
    ax.set_ylabel('Probabilidad')
    ax.legend(bbox_to_anchor=(0.75, 0.99), loc='upper left', borderaxespad=0.)
    ax.grid(True)
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # [Rest of the function remains the same...]

# [Rest of the code remains the same...]
