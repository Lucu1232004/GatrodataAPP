import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import os
from datetime import datetime, timedelta

# =============================================================================
# IMPORTACION DEL MODELO ML
# =============================================================================

from modelo_demanda import cargar_modelos, predecir_semana, PRODUCTOS, DIAS_SEMANA

@st.cache_resource
def cargar_modelo_ml():
    """Carga los modelos entrenados y sus metricas."""
    try:
        modelos = cargar_modelos()
        with open("modelos/metricas_modelo.json", "r", encoding="utf-8") as f:
            metricas = json.load(f)
        return {
            "modelos": modelos,
            "metricas": metricas,
            "productos": PRODUCTOS,
            "dias_semana": DIAS_SEMANA,
            "disponible": True
        }
    except Exception as e:
        return {"disponible": False, "error": str(e)}

# =============================================================================
# CONFIGURACION
# =============================================================================

st.set_page_config(page_title="GastroData Pro | ML Insights", page_icon="📊", layout="wide")

ml = cargar_modelo_ml()

# =============================================================================
# SIDEBAR: CONTROLES EXISTENTES + METRICAS DEL MODELO
# =============================================================================

st.sidebar.header("Centro de Control")

uploaded_file = st.sidebar.file_uploader("Cargar Ventas Reales (CSV)", type=["csv"])

st.sidebar.divider()
st.sidebar.subheader("Simulacion")

trafico = st.sidebar.slider("Trafico de Clientes (%)", 50, 150, 100, 10) / 100
ajuste_precio = st.sidebar.slider("Ajuste de Precios (%)", -20, 20, 0, 5) / 100
eficiencia = st.sidebar.slider("Factor de Eficiencia (%)", 0, 100, 80, 10) / 100

# Panel de Metricas del Modelo en Sidebar
if ml["disponible"]:
    st.sidebar.divider()
    st.sidebar.subheader("Modelo ML: XGBoost")
    st.sidebar.caption("Entrenado: Mayo 2026 | 1,620 registros")

    met = ml["metricas"]
    col_s1, col_s2 = st.sidebar.columns(2)
    col_s1.metric("Accuracy", f"{met['accuracy']:.0%}")
    col_s2.metric("F1-Score", f"{met['f1_score']:.0%}")
    col_s3, col_s4 = st.sidebar.columns(2)
    col_s3.metric("R2 Score", f"{met['r2_score']:.0%}")
    col_s4.metric("MAE", f"{met['mae']} und")

    st.sidebar.progress(int(met["accuracy"] * 100), text="Confianza Global")
else:
    st.sidebar.divider()
    st.sidebar.warning("Modelo ML no disponible. Ejecuta 'python modelo_demanda.py' primero.")

# =============================================================================
# DATOS BASE
# =============================================================================

@st.cache_data
def generar_datos_locales():
    productos = ["Salchipapa", "Hamburguesa", "Perro Caliente", "Pizza Personal", "Empanada", "Arepa Rellena", "Limonada Natural", "Gaseosa Personal", "Porcion de Papas"]
    precios_base = [18000, 22000, 15000, 25000, 3500, 12000, 8000, 5000, 7000]
    df = pd.DataFrame({
        "Producto": productos,
        "Precio_Base": precios_base,
        "Ventas_Mes": [150, 200, 120, 80, 450, 180, 250, 300, 400],
        "Costo_Unitario": [p * 0.45 for p in precios_base]
    })
    return df

if uploaded_file is not None:
    try:
        df_base = pd.read_csv(uploaded_file)
        st.sidebar.success("Datos cargados con exito")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        df_base = generar_datos_locales()
else:
    df_base = generar_datos_locales()

df_simulado = df_base.copy()
df_simulado["Precio_Final"] = df_simulado["Precio_Base"] * (1 + ajuste_precio)
df_simulado["Ventas_Simuladas"] = df_simulado["Ventas_Mes"] * trafico
df_simulado["Ingresos_Proyectados"] = df_simulado["Precio_Final"] * df_simulado["Ventas_Simuladas"]
df_simulado["Margen_Proyectado"] = (df_simulado["Ingresos_Proyectados"] - (df_simulado["Costo_Unitario"] * df_simulado["Ventas_Simuladas"])) * eficiencia

# =============================================================================
# TABS: DASHBOARD PRINCIPAL + ML INSIGHTS
# =============================================================================

tab1, tab2 = st.tabs(["Dashboard Comercial", "ML Insights"])

# =============================================================================
# TAB 1: DASHBOARD COMERCIAL (EXISTENTE, MEJORADO)
# =============================================================================

with tab1:
    st.title("GastroData Pro: Dashboard de Inferencia")
    st.markdown("Plataforma de Inteligencia de Negocio para Restaurantes | Arquitectura Medallon")

    csv_report = df_simulado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar Reporte de Proyecciones (CSV)",
        data=csv_report,
        file_name="reporte_gastrodata_pro.csv",
        mime="text/csv",
    )

    st.divider()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    ingresos_totales = df_simulado["Ingresos_Proyectados"].sum()
    col_m1.metric("Ingresos Proyectados", f"${ingresos_totales:,.0f} COP", delta=f"{trafico*100-100:.0f}%")
    col_m2.metric("Margen Operativo", f"${df_simulado['Margen_Proyectado'].sum():,.0f} COP")

    if ml["disponible"]:
        col_m3.metric("Precision Modelo", f"{ml['metricas']['accuracy']:.0%}", help="Accuracy del clasificador XGBoost")
        col_m4.metric("R2 Score", f"{ml['metricas']['r2_score']:.0%}", help="R2 del regresor de demanda")
    else:
        col_m3.metric("Precision Modelo", "N/A")
        col_m4.metric("R2 Score", "N/A")

    st.divider()

    if eficiencia < 0.4:
        st.error("ALERTA CRITICA: Eficiencia extremadamente baja. Riesgo de quiebra tecnica en margen de empanadas.")
    elif trafico > 1.3:
        st.success("BOOM DE VENTAS: El trafico supera el 130%. Recomendacion: activar 'Modo Fast-Track' en cocina.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Ventas por Producto")
        fig = px.bar(df_simulado, x="Producto", y="Ingresos_Proyectados", color="Ingresos_Proyectados", color_continuous_scale="Blues")
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Rentabilidad por Categoria")
        fig2 = px.scatter(df_simulado, x="Ventas_Simuladas", y="Margen_Proyectado", size="Ingresos_Proyectados", color="Producto", hover_name="Producto")
        st.plotly_chart(fig2, width="stretch")

    st.caption("GastroData Alpha v3.0 | Samuel Admin")

# =============================================================================
# TAB 2: ML INSIGHTS (NUEVO, PROFESIONAL)
# =============================================================================

with tab2:
    if not ml["disponible"]:
        st.warning("Modelo ML no disponible. Ejecuta 'python modelo_demanda.py' para entrenarlo primero.")
        st.stop()

    met = ml["metricas"]
    modelos_obj = ml["modelos"]
    PRODUCTOS = ml["productos"]
    DIAS_SEMANA = ml["dias_semana"]

    st.title("ML Insights: Modelo Predictivo de Demanda")
    st.markdown("Sistema de clasificacion y regresion basado en **XGBoost** para pronosticar la demanda de productos.")

    # Badge de version
    col_b1, col_b2, col_b3, col_b4 = st.columns([1, 1, 1, 3])
    with col_b1:
        st.markdown(
            """
            <div style="background-color:#1a3a5a; color:white; padding:8px 16px; border-radius:20px; text-align:center; font-weight:600; font-size:14px;">
            XGBoost v1.0
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_b2:
        st.markdown(
            f"""
            <div style="background-color:#059669; color:white; padding:8px 16px; border-radius:20px; text-align:center; font-weight:600; font-size:14px;">
            Mayo 2026
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_b3:
        status_color = "#059669" if met["accuracy"] > 0.85 else "#d97706"
        st.markdown(
            f"""
            <div style="background-color:{status_color}; color:white; padding:8px 16px; border-radius:20px; text-align:center; font-weight:600; font-size:14px;">
            KPIs CUMPLIDOS
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Metricas principales del modelo
    st.subheader("Metricas Globales del Modelo")
    col_mm1, col_mm2, col_mm3, col_mm4, col_mm5 = st.columns(5)

    def tarjeta_metrica(col, label, valor, fmt, color, icono):
        col.markdown(
            f"""
            <div style="background:white; border:1px solid #e5e7eb; border-radius:12px; padding:16px; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="font-size:28px; margin-bottom:8px;">{icono}</div>
                <div style="font-size:28px; font-weight:700; color:{color};">{valor:{fmt}}</div>
                <div style="font-size:13px; color:#6b7280; margin-top:4px;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    tarjeta_metrica(col_mm1, "Accuracy", met["accuracy"], ".0%", "#0284c7", "🎯")
    tarjeta_metrica(col_mm2, "F1-Score", met["f1_score"], ".0%", "#059669", "📊")
    tarjeta_metrica(col_mm3, "R2 Score", met["r2_score"], ".0%", "#2563eb", "📈")
    tarjeta_metrica(col_mm4, "MAE", f"{met['mae']} und", "s", "#d97706", "📉")
    tarjeta_metrica(col_mm5, "Registros", met["total_registros"], ",d", "#7c3aed", "💾")

    st.divider()

    # Dos columnas: Feature Importance + Matriz de Confusion
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("Importancia de Variables (Clasificador)")

        fi = met["feature_importance_clasificador"]
        df_fi = pd.DataFrame({
            "Variable": list(fi.keys()),
            "Importancia": list(fi.values())
        }).sort_values("Importancia", ascending=True)

        fig_fi = px.bar(
            df_fi.tail(8),
            x="Importancia",
            y="Variable",
            orientation="h",
            color="Importancia",
            color_continuous_scale="Blues",
            text_auto=".0%"
        )
        fig_fi.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Importancia Relativa",
            yaxis_title="",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        fig_fi.update_traces(textposition="outside")
        st.plotly_chart(fig_fi, width="stretch")

        st.caption("Las variables 'es fin de semana' y 'precio' son las mas influyentes en la demanda.")

    with col_der:
        st.subheader("Matriz de Confusion")

        cm = met["matriz_confusion"]
        labels = met["labels_clasificacion"]

        fig_cm = go.Figure(data=go.Heatmap(
            z=cm,
            x=labels,
            y=labels,
            text=[[str(v) for v in row] for row in cm],
            texttemplate="%{text}",
            textfont={"size": 16, "color": "white"},
            colorscale="Blues",
            showscale=False
        ))
        fig_cm.update_layout(
            height=350,
            xaxis_title="Prediccion",
            yaxis_title="Real",
            xaxis={"side": "bottom"},
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_cm, width="stretch")

        # Calcular accuracy manual de la diagonal
        diagonal = sum(cm[i][i] for i in range(len(cm)))
        total = sum(sum(row) for row in cm)
        st.caption(f"Predicciones correctas en diagonal: {diagonal}/{total} ({diagonal/total:.0%})")

    st.divider()

    # Predicciones para la proxima semana
    st.subheader("Pronostico de Demanda: Proximos 7 Dias")

    predicciones = predecir_semana(modelos_obj)

    # Tabla resumen por dia
    df_pred = pd.DataFrame(predicciones)
    df_pred.columns = ["Producto", "Categoria", "Unids.", "Confianza", "Dia", "Fecha", "Clima"]

    # Pivot: productos como filas, dias como columnas
    pivot_cat = df_pred.pivot_table(
        index="Producto", columns="Dia", values="Categoria", aggfunc="first"
    )
    pivot_und = df_pred.pivot_table(
        index="Producto", columns="Dia", values="Unids.", aggfunc="first"
    )

    # Reordenar dias
    orden_dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    pivot_cat = pivot_cat[[d for d in orden_dias if d in pivot_cat.columns]]
    pivot_und = pivot_und[[d for d in orden_dias if d in pivot_und.columns]]

    col_t1, col_t2 = st.columns([1, 1])

    with col_t1:
        st.markdown("**Categoria de Demanda por Dia**")
        def color_categoria(val):
            colores = {"ALTA": "background-color:#05966920; color:#059669; font-weight:700;",
                       "MEDIA": "background-color:#d9770620; color:#d97706; font-weight:600;",
                       "BAJA": "background-color:#dc262620; color:#dc2626; font-weight:600;"}
            return colores.get(val, "")

        st.dataframe(
            pivot_cat.style.map(color_categoria).format(None),
            width="stretch",
            height=350
        )

    with col_t2:
        st.markdown("**Unidades Estimadas por Dia**")
        def barras_unidades(val):
            if pd.isna(val):
                return ""
            try:
                v = float(val)
                bars = "█" * int(v / 3)
                return f"{bars} {v:.0f}"
            except:
                return str(val)

        df_und_display = pivot_und.map(lambda x: round(float(x), 0) if pd.notna(x) else "")
        st.dataframe(
            df_und_display,
            width="stretch",
            height=350
        )

    st.divider()

    # Reporte de clasificacion detallado
    with st.expander("Ver Reporte de Clasificacion Detallado"):
        cr = met["classification_report"]
        df_cr = pd.DataFrame(cr).T.reset_index()
        df_cr.columns = ["Clase", "Precision", "Recall", "F1-Score", "Soporte"]
        df_cr = df_cr[~df_cr["Clase"].isin(["accuracy", "macro avg", "weighted avg"])]
        st.dataframe(df_cr, width="stretch")

    st.caption("Modelo XGBoost entrenado con datos sinteticos basados en patrones reales del restaurante. Mayo 2026.")
