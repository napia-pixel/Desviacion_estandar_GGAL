import streamlit as st
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import norm
from datetime import date

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Volatilidad de Acciones",
    page_icon="📈",
    layout="wide"
)

# Título y descripción
st.title("📈 Análisis de Volatilidad y Proyección de Precios")
st.markdown("""
Esta aplicación analiza la volatilidad de acciones y muestra una proyección de posibles precios futuros 
basada en una distribución normal.
""")

def obtener_datos(simbolo, periodo='1y'):
    """
    Obtiene datos históricos de un activo.
    """
    try:
        activo = yf.Ticker(simbolo)
        datos = activo.history(period=periodo)
        if datos.empty:
            st.error(f"No se encontraron datos para el símbolo {simbolo}")
            return None
        return datos
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return None

def calcular_volatilidad(datos, ventana=30):
    """
    Calcula la volatilidad anualizada usando una ventana móvil de 30 días.
    """
    retornos = datos['Close'].pct_change()
    volatilidad = retornos.rolling(window=ventana).std() * np.sqrt(252)
    return volatilidad

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
    
    ax.set_yticklabels([])
    ax.set_title(f'Distribución Normal de Precios Proyectados a {dias_proyeccion} días\n{simbolo}')
    ax.set_xlabel('                             Precio                             by Napia')
    ax.set_ylabel('Probabilidad')
    ax.legend(bbox_to_anchor=(0.75, 0.99), loc='upper left', borderaxespad=0.)
    ax.grid(True)
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Mostrar estadísticas en una tabla
    st.subheader("📊 Estadísticas de Proyección")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Precio Actual", f"${precio_actual:.2f}")
    
    with col2:
        st.metric("Intervalo 68%", f"${conf_68[0]:.2f} - ${conf_68[1]:.2f}")
    
    with col3:
        st.metric("Intervalo 95%", f"${conf_95[0]:.2f} - ${conf_95[1]:.2f}")
    
    with col4:
        st.metric("Intervalo 99%", f"${conf_99[0]:.2f} - ${conf_99[1]:.2f}")

# Sidebar para parámetros
st.sidebar.header("⚙️ Parámetros")

# Input para el símbolo
simbolo = st.sidebar.text_input("Símbolo de la Acción", "GGAL.BA")

# Selector para el período
periodo_opciones = {
    '1 mes': '1mo',
    '3 meses': '3mo',
    '6 meses': '6mo',
    '1 año': '1y',
    '2 años': '2y',
    '5 años': '5y'
}
periodo = st.sidebar.selectbox(
    "Período Histórico",
    options=list(periodo_opciones.keys()),
    index=3
)

# Slider para días de proyección
dias_proyeccion = st.sidebar.slider(
    "Días de Proyección",
    min_value=1,
    max_value=90,
    value=30,
    step=1
)

# Botón para ejecutar el análisis
if st.sidebar.button("Analizar"):
    with st.spinner("Calculando proyecciones..."):
        graficar_distribucion_normal(
            simbolo,
            dias_proyeccion=dias_proyeccion,
            periodo=periodo_opciones[periodo]
        )

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📝 Notas:
- Los cálculos se basan en la volatilidad histórica
- Se asume una distribución normal de retornos
- Los intervalos muestran rangos de precios probables
""")
