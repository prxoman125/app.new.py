# =========================================================================
# MÓDULO DE FÍSICA Y ÓPTICA: physics_engine.py
# Descripción: Contiene los modelos matemáticos y físicos para cálculos 
# de óptica coherente, divergencia de haces láser, correcciones atmosféricas
# y análisis estadístico de incertidumbre para el simulador del CIO.
# =========================================================================

import numpy as np
import math
from scipy import stats

def calcular_propagacion_gausiana(w0_mm, wavelength_nm, z_max_m, num_points=100):
    """
    Calcula el perfil de propagación de un haz láser gaussiano TEM_00.
    
    Parámetros:
    - w0_mm: Radio de cintura del haz en milímetros (mm).
    - wavelength_nm: Longitud de onda en nanómetros (nm).
    - z_max_m: Distancia máxima de propagación en metros (m).
    - num_points: Número de puntos para la discretización del eje z.
    
    Retorna:
    - z_arr: Arreglo de posiciones a lo largo del eje z (m).
    - w_z_mm: Ancho del haz w(z) en milímetros (mm).
    - zr_m: Rango de Rayleigh en metros (m).
    """
    # Conversión de unidades a SI (metros)
    w0 = w0_mm * 1e-3
    wavelength = wavelength_nm * 1e-9
    
    # Rango de Rayleigh (z_R = pi * w0^2 / lambda)
    zr = (math.pi * (w0 ** 2)) / wavelength
    
    # Eje z desde 0 hasta z_max_m
    z_arr = np.linspace(0, z_max_m, num_points)
    
    # Perfil del haz w(z) = w0 * sqrt(1 + (z / z_R)^2) en metros
    w_z_m = w0 * np.sqrt(1.0 + (z_arr / zr) ** 2)
    
    # Convertir de vuelta a milímetros para visualización
    w_z_mm = w_z_m * 1e3
    
    return z_arr, w_z_mm, zr

def calcular_correccion_atmosferica(distancia_m, temperatura_c, presion_hpa, humedad_pct):
    """
    Calcula la refracción atmosférica y el desplazamiento aparente del haz 
    debido a gradientes de temperatura y presión (Índice de refracción del aire n).
    
    Fórmula de Edlén modificada / aproximación estándar para el índice de refracción del aire:
    (n - 1) * 1e6 = 77.6 * (P / T) + ...
    
    Retorna:
    - n_aire: Índice de refracción del aire.
    - desviacion_mm: Desplazamiento lineal estimado en mm debido a la refracción en la distancia dada.
    """
    T_kelvin = temperatura_c + 273.15
    # Fórmula aproximada de refractividad (N = (n-1)*1e6)
    # N = 77.6 * (P / T) [K, hPa]
    refractividad = 77.6 * (presion_hpa / T_kelvin)
    n_aire = 1.0 + (refractividad * 1e-6)
    
    # Desviación estimada basada en gradiente refractivo hipotético lineal sobre la distancia
    # (modelo simplificado para simulación de metrología óptica)
    factor_gradiente = (n_aire - 1.0) * 0.05
    desviacion_mm = distancia_m * factor_gradiente * 1e3
    
    return n_aire, desviacion_mm

def analizar_incertidumbre_mediciones(datos_medicion):
    """
    Realiza un análisis estadístico de incertidumbre sobre un arreglo de mediciones ópticas.
    
    Parámetros:
    - datos_medicion: Lista o arreglo de valores numéricos de mediciones.
    
    Retorna:
    - media: Promedio aritmético.
    - desviacion_estandar: Desviación estándar muestral (s).
    - incertidumbre_tipica: Error estándar de la media (SEM = s / sqrt(N)).
    - intervalo_confianza_95: Intervalo de confianza al 95% usando t-Student.
    """
    arr = np.array(datos_medicion)
    if len(arr) == 0:
        return 0.0, 0.0, 0.0, (0.0, 0.0)
        
    n = len(arr)
    media = np.mean(arr)
    desviacion_estandar = np.std(arr, ddof=1) if n > 1 else 0.0
    
    # Error estándar de la media
    incertidumbre_tipica = (desviacion_estandar / math.sqrt(n)) if n > 0 else 0.0
    
    # Intervalo de confianza del 95% (t-Student)
    if n > 1:
        t_critico = stats.t.ppf(0.975, df=n-1)
        margen_error = t_critico * incertidumbre_tipica
        intervalo_confianza_95 = (media - margen_error, media + margen_error)
    else:
        intervalo_confianza_95 = (media, media)
        
    return float(media), float(desviacion_estandar), float(incertidumbre_tipica), (float(intervalo_confianza_95[0]), float(intervalo_confianza_95[1]))
