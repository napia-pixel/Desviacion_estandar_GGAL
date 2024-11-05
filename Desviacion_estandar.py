import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import norm
from datetime import date

def obtener_datos(simbolo, periodo='1y'):
    """
    Obtiene datos históricos de un activo.
    """
    activo = yf.Ticker(simbolo)
    datos = activo.history(period=periodo)
    return datos

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
    
    Args:
        simbolo (str): Símbolo del activo
        dias_proyeccion (int): Número de días hacia el futuro para la proyección
        periodo (str): Período histórico para calcular la volatilidad
    """
    # Obtener datos y calcular volatilidad
    datos = obtener_datos(simbolo, periodo)
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
    plt.figure(figsize=(10, 8))
    plt.plot(rango_precios, distribucion, 'b-', lw=2, label='Distribución de precios')
    
    # Agregar áreas sombreadas para los intervalos de confianza
    plt.fill_between(rango_precios, distribucion, 
                     where=(rango_precios >= conf_68[0]) & (rango_precios <= conf_68[1]),
                     color='blue', alpha=0.3, 
                     label=f'68%: ${conf_68[0]:.2f} - ${conf_68[1]:.2f}')
    plt.fill_between(rango_precios, distribucion, 
                     where=(rango_precios >= conf_95[0]) & (rango_precios <= conf_95[1]),
                     color='blue', alpha=0.2, 
                     label=f'95%: ${conf_95[0]:.2f} - ${conf_95[1]:.2f}')
    plt.fill_between(rango_precios, distribucion, 
                     where=(rango_precios >= conf_99[0]) & (rango_precios <= conf_99[1]),
                     color='blue', alpha=0.1, 
                     label=f'99%: ${conf_99[0]:.2f} - ${conf_99[1]:.2f}')

    plt.axvline(precio_actual, color='red', linestyle='--', 
                label=f'Precio actual: ${precio_actual:.2f}')
    
    plt.gca().set_yticklabels([])
    plt.title(f'Distribución Normal de Precios Proyectados a {dias_proyeccion} días\n{simbolo}')
    plt.xlabel('Precio')
    plt.ylabel('Probabilidad')
    plt.legend(bbox_to_anchor=(0.75, 0.99), loc='upper left', borderaxespad=0.) #para correr de lugar el cuadro de datos
    plt.grid(True)
    plt.tight_layout()

    # Imprimir estadísticas también en consola
    print(f"\nEstadísticas de proyección para {simbolo} a {dias_proyeccion} días:")
    print(f"Precio actual: ${precio_actual:.2f}")
    print(f"\nIntervalos de confianza:")
    print(f"68% de probabilidad: ${conf_68[0]:.2f} - ${conf_68[1]:.2f}")
    print(f"95% de probabilidad: ${conf_95[0]:.2f} - ${conf_95[1]:.2f}")
    print(f"99% de probabilidad: ${conf_99[0]:.2f} - ${conf_99[1]:.2f}")

    plt.show()

# Ejemplo de uso
if __name__ == "__main__":
    # Graficar distribución
    graficar_distribucion_normal("GGAL.BA", dias_proyeccion=30)
