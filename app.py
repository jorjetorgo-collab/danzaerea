import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE IDENTIDAD (M0) ---
st.set_page_config(page_title="Ley de Conservación de Identidad - M0", layout="wide")

def generar_simulacion():
    # Variables de la Ley de Conservación (Teorema de Torres)
    n_drones = 52
    v_kmh = 60
    v_ms = v_kmh / 3.6
    radio_giro = 2.0         # ΔΦ: Diferencial de fase proyectado en 2m
    desfase_us = 3           # Diferencial de fase entre unidades (3 microsegundos)
    ancho_campo = 2000       # 2 km
    largo_total = 8000       # 8 km
    paso_tiempo = 0.1        
    
    placeholder = st.empty()
    
    # Fase 1: IDA (Trayectoria de expansión)
    for t in np.arange(0, 50, paso_tiempo):
        puntos = []
        for i in range(n_drones):
            # Aplicación del Trayector (ΣΔΦ)
            t_unidad = t - (i * desfase_us / 1_000_000)
            
            if t_unidad > 0:
                y_progreso = v_ms * t_unidad
                omega = 2 * np.pi * 0.5  
                sentido = 1 if i < 26 else -1
                
                dx = np.cos(omega * t_unidad) * radio_giro * sentido
                dy_extra = np.sin(omega * t_unidad) * radio_giro
                x_base = (i / (n_drones - 1)) * ancho_campo - (ancho_campo / 2)
                
                puntos.append({
                    'Unidad': i,
                    'Latitud (X)': x_base + dx,
                    'Longitud (Y)': y_progreso + dy_extra,
                    'Flanco': 'Izquierdo' if i < 26 else 'Derecho'
                })
        
        if puntos:
            df = pd.DataFrame(puntos)
            with placeholder.container():
                st.subheader("Auditoría del Horizonte: Fase de Ida")
                st.scatter_chart(df, x='Latitud (X)', y='Longitud (Y)', color='Flanco', size=30)
        time.sleep(0.01)

    st.warning("Reagrupando: Iniciando Proceso de Desentropía (Inversión de Fase)")
    time.sleep(1)

    # Fase 2: REGRESO (Desentropía Operativa)
    for t in np.arange(50, 0, -paso_tiempo):
        puntos = []
        for i in range(n_drones):
            t_unidad = t - (i * desfase_us / 1_000_000)
            
            if t_unidad > 0:
                y_progreso = v_ms * t_unidad
                omega = 2 * np.pi * 0.5
                sentido = -1 if i < 26 else 1
                
                dx = np.cos(omega * t_unidad) * radio_giro * sentido
                dy_extra = np.sin(omega * t_unidad) * radio_giro
                x_base = (i / (n_drones - 1)) * ancho_campo - (ancho_campo / 2)
                
                puntos.append({
                    'Unidad': i,
                    'Latitud (X)': x_base + dx,
                    'Longitud (Y)': y_progreso + dy_extra,
                    'Flanco': 'Izquierdo' if i < 26 else 'Derecho'
                })
        
        if puntos:
            df = pd.DataFrame(puntos)
            with placeholder.container():
                st.subheader("Auditoría del Horizonte: Fase de Regreso")
                st.scatter_chart(df, x='Latitud (X)', y='Longitud (Y)', color='Flanco', size=30)
        time.sleep(0.01)

# --- INTERFAZ ---
st.title("🛡️ Sistema de Trayectoria Inviolable")
st.write("Implementación del **Teorema de Torres** para la navegación de enjambres basada en la conservación de la identidad ($M_0$).")

if st.button("Ejecutar Trayector (ΣΔΦ)"):
    generar_simulacion()
