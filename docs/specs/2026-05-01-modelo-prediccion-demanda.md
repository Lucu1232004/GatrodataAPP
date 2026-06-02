# Especificacion: Modelo de Prediccion de Demanda para GastroData

## Objetivo
Implementar un modelo de machine learning real que prediga la demanda de productos en un restaurante, integrado profesionalmente en el dashboard GastroData. Debe cumplir accuracy > 0.85, F1-score > 0.85, R2 > 0.85.

## Arquitectura del Modelo

### Dos modelos complementarios:

| Modelo | Tipo | Target | Metrica |
|--------|------|--------|---------|
| Clasificador | Multiclase (Random Forest / XGBoost) | Categoria de demanda: ALTA (>30 und), MEDIA (15-30), BAJA (<15) | Accuracy > 0.85, F1-score > 0.85 |
| Regresor | Continuo (Random Forest / XGBoost) | Unidades exactas a vender | R2 > 0.85 |

### Features de entrada (8-10):
- Precio unitario
- Costo unitario
- Margen porcentual
- Dia de la semana (one-hot encoding)
- Es fin de semana (binario)
- Categoria del producto (label encoding)
- Precio promedio de la categoria
- Clima simulado (Soleado/Lluvioso/Nublado)
- Es festivo (binario)

## Datos Sinteticos
Se generaran ~5000 registros con patrones realistas basados en los CSVs de entregables_oro:
- Mismos 9 productos y 4 categorias
- Rangos de precios y costos identicos
- Patrones de fin de semana (sabado/domingo ~60% mas ventas)
- Distribucion de clima (30% lluvioso, 50% soleado, 20% nublado)
- Ruido controlado (+/- 15%) para evitar overfitting

## Archivos a crear/modificar

```
modelo_demanda.py        - Script principal con clase DemandPredictor
app.py                   - Nuevo panel "ML Insights" en Streamlit
modelos/                 - Modelos guardados (.pkl) + metricas.json
```

### modelo_demanda.py:
- `generar_datos_sinteticos()` -> DataFrame con features + targets
- `entrenar_modelos(df)` -> entrena clasificador y regresor, evalua
- `guardar_modelos()` -> exporta .pkl y metricas.json
- `cargar_modelos()` -> carga modelos guardados
- `predecir_demanda(producto, dia, clima)` -> prediccion individual

### app.py (Streamlit):
- Sidebar nueva: "ML Insights"
- Tarjetas con Accuracy, F1, R2
- Grafico de feature importance
- Tabla de predicciones para los proximos 7 dias
- Badge con version del modelo y fecha de entrenamiento

### metricas.json:
```json
{
  "accuracy": 0.89,
  "f1_score": 0.87,
  "r2_score": 0.91,
  "fecha_entrenamiento": "2026-05-01",
  "modelo": "XGBoost",
  "features": [...],
  "feature_importance": {...},
  "classification_report": {...}
}
```

## Visualizacion Profesional
- Colores corporativos (azul petroleo #0284c7, esmeralda #059669)
- Matriz de confusion con plotly heatmap
- Feature importance con barras horizontales
- Predicciones con progress bar de confianza
- Tipografia limpia (Outfit, misma del dashboard)

## Flujo de uso
1. El usuario ejecuta `python modelo_demanda.py` -> genera datos, entrena, evalua, guarda
2. `app.py` carga los modelos y muestra predicciones en vivo
3. Los modelos se pueden re-entrenar con nuevos datos cuando se quiera

## Criterio de exito
- Accuracy del clasificador > 0.85
- F1-score ponderado > 0.85
- R2 del regresor > 0.85
- Dashboard muestra metricas, graficos y predicciones funcionales
