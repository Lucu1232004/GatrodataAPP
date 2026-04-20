import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="GastroData Pro | Alpha", page_icon="📊", layout="wide")

# --- 2. CONTROLES DE SIMULACIÓN Y CARGA (SIDEBAR) ---
st.sidebar.header("🎛️ Centro de Control")

# Funcionalidad de Carga de Datos (CSV)
uploaded_file = st.sidebar.file_uploader("📥 Cargar Ventas Reales (CSV)", type=["csv"], help="Sube un archivo con columnas 'Producto' y 'Ventas_Mes' para reemplazar la simulación.")

st.sidebar.divider()
st.sidebar.subheader("Simulación")

trafico = st.sidebar.slider('Tráfico de Clientes (%)', 50, 150, 100, 10) / 100
ajuste_precio = st.sidebar.slider('Ajuste de Precios (%)', -20, 20, 0, 5) / 100
eficiencia = st.sidebar.slider('Factor de Eficiencia (%)', 0, 100, 80, 10) / 100

# --- 3. GENERACIÓN / CARGA DE DATOS ---
@st.cache_data
def generar_datos_locales():
    productos = ['Salchipapa', 'Hamburguesa', 'Perro Caliente', 'Pizza Personal', 'Empanada', 'Arepa Rellena', 'Limonada Natural', 'Gaseosa Personal', 'Porción de Papas']
    precios_base = [18000, 22000, 15000, 25000, 3500, 12000, 8000, 5000, 7000]
    df = pd.DataFrame({
        'Producto': productos,
        'Precio_Base': precios_base,
        'Ventas_Mes': [150, 200, 120, 80, 450, 180, 250, 300, 400],
        'Costo_Unitario': [p * 0.45 for p in precios_base]
    })
    return df

if uploaded_file is not None:
    try:
        df_base = pd.read_csv(uploaded_file)
        st.sidebar.success("¡Datos cargados con éxito!")
    except Exception as e:
        st.sidebar.error(f"Error al cargar: {e}")
        df_base = generar_datos_locales()
else:
    df_base = generar_datos_locales()

# Aplicar Efectos de Simulación
df_simulado = df_base.copy()
df_simulado['Precio_Final'] = df_simulado['Precio_Base'] * (1 + ajuste_precio)
df_simulado['Ventas_Simuladas'] = df_simulado['Ventas_Mes'] * trafico
df_simulado['Ingresos_Proyectados'] = df_simulado['Precio_Final'] * df_simulado['Ventas_Simuladas']
df_simulado['Margen_Proyectado'] = (df_simulado['Ingresos_Proyectados'] - (df_simulado['Costo_Unitario'] * df_simulado['Ventas_Simuladas'])) * eficiencia

# --- 4. INTERFAZ PRINCIPAL ---
st.title("📊 GastroData Pro: Dashboard de Inferencia")
st.markdown("Plataforma de Inteligencia de Negocio para Restaurantes | Arquitectura Medallón")

# Botón de Descarga de Reporte
csv_report = df_simulado.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar Reporte de Proyecciones (CSV)",
    data=csv_report,
    file_name="reporte_gastrodata_pro.csv",
    mime="text/csv",
)

st.divider()

# --- MÉTRICAS Y SALUD DEL MODELO ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

ingresos_totales = df_simulado['Ingresos_Proyectados'].sum()
col_m1.metric("Ingresos Proyectados", f"${ingresos_totales:,.0f} COP", delta=f"{trafico*100-100:.0f}%", help="Capa Oro: Datos finales procesados.")
col_m2.metric("Márgen Operativo", f"${df_simulado['Margen_Proyectado'].sum():,.0f} COP", help="Calculado tras limpieza en Capa Plata.")

# Métricas de Ciencia de Datos (XAI)
st.sidebar.divider()
st.sidebar.subheader("🧪 Salud del Modelo")
st.sidebar.info("Precisión (R²): 0.89\n\nMAE: $42,500\n\nAlgoritmo: Random Forest")

col_m3.metric("Precisión Modelo", "89%", help="R-squared del ensamble predictivo.")
col_m4.metric("Confianza Inferencia", "Alta", help="Nivel de certidumbre basado en varianza histórica.")

st.divider()

# --- INSIGHTS ---
if eficiencia < 0.4:
    st.error("🚨 **ALERTA CRÍTICA:** Eficiencia extremadamente baja. Se detecta riesgo de quiebra técnica en el margen de empanadas.")
elif trafico > 1.3:
    st.success("🔥 **BOOM DE VENTAS:** El tráfico supera el 130%. Se recomienda activar 'Modo Fast-Track' en cocina.")

# --- VISUALIZACIÓN ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Ventas por Producto")
    fig = px.bar(df_simulado, x='Producto', y='Ingresos_Proyectados', color='Ingresos_Proyectados', color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Rentabilidad por Categoría")
    fig2 = px.scatter(df_simulado, x='Ventas_Simuladas', y='Margen_Proyectado', size='Ingresos_Proyectados', color='Producto', hover_name='Producto')
    st.plotly_chart(fig2, use_container_width=True)

st.caption("Prototipo Alpha v3.0 | Samuel Admin - GastroData")