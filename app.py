import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE IDENTIDAD (M0) ---
st.set_page_config(page_title="Ley de Conservación de Identidad - M0", layout="wide")

st.sidebar.header("Control del Trayector (Mn)")
v_kmh = st.sidebar.slider("Velocidad (km/h)", 10, 150, 60)
radio_elipse = st.sidebar.slider("Radio de Órbita (m)", 1, 20, 5)

def generar_simulacion(v_kmh, radio_elipse):
    n_drones = 52
    v_ms = v_kmh / 3.6
    desfase_us = 3           # ΔΦ: Diferencial de fase [cite: 10]
    ancho_campo = 2000       
    largo_total = 8000       
    paso_tiempo = 0.2        
    
    placeholder = st.empty()
    
    # --- FASE 1: IDA CON CRUCE DE TRAYECTORIA ---
    for t in np.arange(0, 60, paso_tiempo):
        puntos = []
        for i in range(n_drones):
            t_unidad = t - (i * desfase_us / 1_000_000)
            if t_unidad > 0:
                # Progresión de cruce (Inversión de flanco proporcional al tiempo)
                # Al final del tiempo (t=60), el factor de cruce es 1 (inversión total)
                factor_cruce = min(t / 50, 1.0) 
                
                # Posición X inicial vs final (Inversa)
                x_inicio = (i / (n_drones - 1)) * ancho_campo - (ancho_campo / 2)
                x_fin = -x_inicio # Lado inverso proporcional
                x_actual = x_inicio + (x_fin - x_inicio) * factor_cruce
                
                # Geometría de Punta (V)
                dist_centro = abs(i - 25.5)
                y_base = (v_ms * t_unidad) - (dist_centro * 15)
                
                # Órbita Elíptica (Giro)
                omega = 2 * np.pi * 0.4
                sentido = 1 if i < 26 else -1
                dx = np.cos(omega * t_unidad) * radio_elipse * sentido
                dy_o = np.sin(omega * t_unidad) * (radio_elipse * 0.5)
                
                puntos.append({
                    'ID': i,
                    'X': x_actual + dx,
                    'Y': y_base + dy_o,
                    'Flanco': 'Original Izq' if i < 26 else 'Original Der'
                })
        
        if puntos:
            df = pd.DataFrame(puntos)
            with placeholder.container():
                st.subheader("Auditoría: Maniobra de Inversión Trayectorial")
                st.scatter_chart(df, x='X', y='Y', color='Flanco', size=40)
        time.sleep(0.01)

    st.success("Igualación Final Alcanzada: Posiciones Invertidas.")
    time.sleep(1)

    # --- FASE 2: REGRESO FIJO (Sin trayectoria inversa) ---
    for t in np.arange(60, 0, -paso_tiempo):
        puntos = []
        for i in range(n_drones):
            t_unidad = t - (i * desfase_us / 1_000_000)
            if t_unidad > 0:
                # Mantenemos la posición X invertida fija
                x_invertida = -((i / (n_drones - 1)) * ancho_campo - (ancho_campo / 2))
                y_base = (v_ms * t_unidad) - (abs(i - 25.5) * 15)
                
                puntos.append({
                    'ID': i, 'X': x_invertida, 'Y': y_base, 'Flanco': 'Retorno Fijo'
                })
        
        if puntos:
            df = pd.DataFrame(puntos)
            with placeholder.container():
                st.subheader("Fase de Regreso: Identidad Conservada en Espejo")
                st.scatter_chart(df, x='X', y='Y', color='Flanco', size=40)
        time.sleep(0.01)

# --- LANZAMIENTO ---
st.write("Cálculo de **Desentropía de Torres** ($D$) aplicado al cruce de flancos.")
if st.button("Activar Protocolo de Cruce"):
    generar_simulacion(v_kmh, radio_elipse)
