import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE IDENTIDAD (M0) ---
st.set_page_config(page_title="Ley de Conservación de Identidad - M0", layout="wide")

# --- INTERFAZ DE CONTROL (DEMONIO DE LAPLACE) ---
st.title("🛡️ Sistema de Trayectoria Inviolable")
st.sidebar.header("Parámetros del Trayector (Mn)")

# Variables manipulables por el usuario
v_kmh = st.sidebar.slider("Velocidad de Reconocimiento (km/h)", 10, 150, 60)
radio_elipse = st.sidebar.slider("Radio de la Órbita (Metros)", 1, 20, 5)
ver_estela = st.sidebar.checkbox("Mostrar Estela (Identidad Conservada)", True)

def generar_simulacion(v_kmh, radio_elipse):
    n_drones = 52
    v_ms = v_kmh / 3.6
    desfase_us = 3           # ΔΦ: Diferencial de fase (3 microsegundos)
    ancho_campo = 2000       # 2 km
    largo_total = 8000       # 8 km
    paso_tiempo = 0.1        
    
    placeholder = st.empty()
    
    # Fase 1: IDA
    for t in np.arange(0, 60, paso_tiempo):
        puntos = []
        for i in range(n_drones):
            # 1. Trayector de Tiempo (ΣΔΦ)
            t_unidad = t - (i * desfase_us / 1_000_000)
            
            if t_unidad > 0:
                # 2. Geometría de Formación (Punta Central y Alas)
                # Calculamos un retraso en Y proporcional a la distancia al centro
                distancia_al_centro = abs(i - 25.5)
                retraso_ala = distancia_al_centro * 15 # 15 metros de retraso por unidad hacia afuera
                
                y_base = (v_ms * t_unidad) - retraso_ala
                
                # 3. Órbita Elíptica (Giro de 5m)
                omega = 2 * np.pi * 0.4 # Frecuencia de órbita
                sentido = 1 if i < 26 else -1
                
                # El trayector ajusta el desfase de giro para evitar colisiones laterales
                dx = np.cos(omega * t_unidad) * radio_elipse * sentido
                dy_orbita = np.sin(omega * t_unidad) * (radio_elipse * 0.5) # Elipse
                
                # Posición base X
                x_base = (i / (n_drones - 1)) * ancho_campo - (ancho_campo / 2)
                
                puntos.append({
                    'Unidad': i,
                    'Latitud (X)': x_base + dx,
                    'Longitud (Y)': y_base + dy_orbita,
                    'Flanco': 'Izquierdo' if i < 26 else 'Derecho'
                })
        
        if puntos:
            df = pd.DataFrame(puntos)
            with placeholder.container():
                st.subheader(f"Auditoría del Horizonte: {v_kmh} km/h | Órbita: {radio_elipse}m")
                # Gráfico con límites dinámicos
                st.scatter_chart(df, x='Latitud (X)', y='Longitud (Y)', color='Flanco', size=40)
        
        time.sleep(0.01)

# --- EJECUCIÓN ---
st.write("Ajuste del **Trayector** para asegurar que la incertidumbre sea técnicamente cero mediante el control de variables de fase.")

if st.button("Lanzar Enjambre (Axioma Operativo)"):
    generar_simulacion(v_kmh, radio_elipse)
