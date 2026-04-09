import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE IDENTIDAD (M0) ---
st.set_page_config(page_title="Ley de Conservación de Identidad - M0", layout="wide")

st.sidebar.header("Parámetros del Trayector (Mn)")
v_kmh = st.sidebar.slider("Velocidad (km/h)", 10, 150, 60)
radio_elipse = st.sidebar.slider("Radio de Órbita (m)", 1, 20, 8) # Aumentado para visibilidad

def generar_simulacion(v_kmh, radio_elipse):
    n_drones = 52
    v_ms = v_kmh / 3.6
    desfase_us = 3           # ΔΦ: Diferencial de fase (invariante estructural)
    ancho_campo = 2000       
    largo_total = 8000       
    paso_tiempo = 0.2        
    
    placeholder = st.empty()
    
    # --- FASE 1: IDA (CRUCE SIGMOIDAL SUAVE) ---
    # Usamos una función sigmoide para que el cruce sea gradual y visible
    for t in np.arange(0, 60, paso_tiempo):
        puntos = []
        for i in range(n_drones):
            t_unidad = t - (i * desfase_us / 1_000_000)
            if t_unidad > 0:
                y_base = v_ms * t_unidad
                
                # Proceso de igualación final: El cruce ocurre suavemente en el medio
                # factor_cruce va de 0 a 1 usando una curva sigmoide
                factor_cruce = 1 / (1 + np.exp(-0.2 * (y_base - 4000/v_ms))) 
                
                x_inicio = (i / (n_drones - 1)) * ancho_campo - (ancho_campo / 2)
                x_fin = -x_inicio 
                x_actual = x_inicio + (x_fin - x_inicio) * (t / 60) # Transición lineal más lenta
                
                # Geometría de Punta (V) - Invariante Estructural
                dist_centro = abs(i - 25.5)
                y_pos = y_base - (dist_centro * 15)
                
                # Órbita Elíptica (Giro visible)
                omega = 2 * np.pi * 0.3
                sentido = 1 if i < 26 else -1
                dx = np.cos(omega * t_unidad) * radio_elipse * sentido
                dy_o = np.sin(omega * t_unidad) * (radio_elipse * 0.5)
                
                puntos.append({
                    'ID': i,
                    'X': x_actual + dx,
                    'Y': y_pos + dy_o,
                    'Flanco': 'Original Izq' if i < 26 else 'Original Der'
                })
        
        if puntos:
            df = pd.DataFrame(puntos)
            with placeholder.container():
                st.subheader("Auditoría: Avance con Cruce de Fase Proporcional")
                st.scatter_chart(df, x='X', y='Y', color='Flanco', size=40)
        time.sleep(0.01)

    st.success("Igualación Final Alcanzada: Posiciones en Espejo.")
    time.sleep(1.5)

    # --- FASE 2: REGRESO (PINZA ABIERTA - DESENTROPÍA) ---
    for t in np.arange(60, 0, -paso_tiempo):
        puntos = []
        for i in range(n_drones):
            t_unidad = t - (i * desfase_us / 1_000_000)
            if t_unidad > 0:
                # Regresan en la posición X invertida fija (Pinza)
                x_invertida = -((i / (n_drones - 1)) * ancho_campo - (ancho_campo / 2))
                y_base = (v_ms * t_unidad) - (abs(i - 25.5) * 15)
                
                puntos.append({
                    'ID': i, 'X': x_invertida, 'Y': y_base, 'Flanco': 'Retorno Conservado'
                })
        
        if puntos:
            df = pd.DataFrame(puntos)
            with placeholder.container():
                st.subheader("Fase de Regreso: Pinza de Identidad Conservada (M0)")
                st.scatter_chart(df, x='X', y='Y', color='Flanco', size=40)
        time.sleep(0.01)

# --- LANZAMIENTO ---
if st.button("Activar Auditoría del Horizonte"):
    generar_simulacion(v_kmh, radio_elipse)
