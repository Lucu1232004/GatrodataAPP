# GastroData Intelligence: Prototipo Alpha

**Proyecto Final - Curso: Data Thinking**  
**Desarrollador:** Samuel Admin  
**Objetivo:** Sistema de Gestión Inteligente y Analítica Predictiva para Restaurantes.

---

## Descripción del Proyecto
GastroData es una solución analítica de extremo a extremo que utiliza una **Arquitectura Medallón** para transformar datos transaccionales en bruto en inferencias estratégicas. El objetivo principal es optimizar el inventario y maximizar la rentabilidad mediante el uso de modelos predictivos de demanda.

## Arquitectura de Datos (Medallion)
El proyecto implementa las tres capas fundamentales para garantizar la integridad y utilidad de los datos:

1.  **Capa Bronce (Raw):** Ingesta de tickets de venta en tiempo real (simulada en `script.js` y generada en el notebook).
2.  **Capa Plata (Silver):** Procesamiento, limpieza y agregación de datos por día y producto. Cálculo de costos vs. ingresos.
3.  **Capa Oro (Gold):** KPIs de negocio consolidados (Ingresos Totales, Margen Operativo) y entrada para el motor de inferencia.

## Metodología y Ciencia de Datos
-   **Modelado Predictivo:** Se utiliza un ensamble de **Random Forest Regressor** (simulado en el prototipo) para proyectar las ventas de la próxima semana, considerando estacionalidad (fines de semana), clima y días festivos.
-   **Toma de Decisiones (AHP):** Se aplicó el método de *Proceso de Jerarquía Analítica* para priorizar el desarrollo de funciones, seleccionando la "Optimización de Inventario" como el pilar de mayor impacto.
-   **Inferencia Dinámica:** El sistema genera alertas automáticas basadas en el cruce de variables ambientales y capacidad operativa.

## Funcionalidades Clave
-   **Dashboard Interactivo:** Visualización en tiempo real de KPIs y tendencias.
-   **Simulador de Escenarios:** Controladores para ajustar Tráfico y Precios, observando el impacto financiero instantáneamente.
-   **Carga de Datos:** Soporte para subir archivos CSV propios y procesar ventas reales.
-   **Exportación:** Generación de reportes predictivos descargables.

## Cómo Ejecutar el Proyecto

### Opción A: Dashboard Web (HTML/JS)
1. Abrir una terminal en la carpeta del proyecto.
2. Ejecutar: `python -m http.server 8000`
3. Abrir en el navegador: `http://localhost:8000`

### Opción B: Dashboard Analítico (Streamlit)
1. Asegurarse de tener Python instalado.
2. Instalar dependencias: `pip install streamlit pandas plotly`
3. Ejecutar: `streamlit run app.py`

---
**GastroData Alpha v3.0** | *Transformando datos en decisiones sabrosas.*
