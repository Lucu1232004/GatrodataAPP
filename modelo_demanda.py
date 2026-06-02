"""
modelo_demanda.py - Modelo Predictivo de Demanda para GastroData
Entrena un clasificador (categoria ALTA/MEDIA/BAJA) y un regresor (unidades exactas)
con datos sinteticos basados en los patrones reales del restaurante.

Autor: Samuel Admin
Fecha: Mayo 2026
"""

import pandas as pd
import numpy as np
import json
import os
import warnings
from datetime import datetime, timedelta

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report,
    confusion_matrix, r2_score, mean_absolute_error,
    mean_squared_error
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import xgboost as xgb
import joblib

warnings.filterwarnings("ignore")

# =============================================================================
# 1. CATALOGO DE PRODUCTOS (identico al de la app real)
# =============================================================================

PRODUCTOS = {
    "Salchipapa":     {"categoria": "Comida Rapida",  "precio": 18000, "costo": 8100},
    "Hamburguesa":    {"categoria": "Comida Rapida",  "precio": 22000, "costo": 9900},
    "Perro Caliente": {"categoria": "Comida Rapida",  "precio": 15000, "costo": 6750},
    "Pizza Personal": {"categoria": "Comida Rapida",  "precio": 25000, "costo": 11250},
    "Empanada":       {"categoria": "Tradicional",    "precio": 3500,  "costo": 1575},
    "Arepa Rellena":  {"categoria": "Tradicional",    "precio": 12000, "costo": 5400},
    "Limonada Natural": {"categoria": "Bebidas",      "precio": 8000,  "costo": 3600},
    "Gaseosa Personal": {"categoria": "Bebidas",      "precio": 5000,  "costo": 2250},
    "Porcion de Papas": {"categoria": "Acompanante",  "precio": 7000,  "costo": 3150},
}

DIAS_SEMANA = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
CLIMAS = ["Soleado", "Lluvioso", "Nublado"]

# =============================================================================
# 2. GENERACION DE DATOS SINTETICOS REALISTAS
# =============================================================================

def generar_datos_sinteticos(n_dias=180, seed=42):
    """
    Genera datos de ventas diarias por producto con patrones realistas.
    Basado en las distribuciones observadas en los CSVs de entregables_oro.
    """
    rng = np.random.RandomState(seed)
    registros = []

    # Fecha de inicio
    fecha_base = datetime(2024, 3, 1)

    for i in range(n_dias):
        fecha = fecha_base + timedelta(days=i)
        dia_semana = DIAS_SEMANA[fecha.weekday()]
        es_fin_semana = 1 if fecha.weekday() >= 5 else 0

        # Clima del dia (con sesgo: findes mas soleados)
        if es_fin_semana:
            clima = rng.choice(CLIMAS, p=[0.60, 0.15, 0.25])
        else:
            clima = rng.choice(CLIMAS, p=[0.40, 0.35, 0.25])

        # Factor base de trafico segun dia
        factores_trafico = {
            "Lunes": 0.85, "Martes": 0.90, "Miercoles": 0.92,
            "Jueves": 0.88, "Viernes": 0.95, "Sabado": 1.45, "Domingo": 1.35
        }
        factor_trafico = factores_trafico[dia_semana]

        # Impacto del clima
        factor_clima = {"Soleado": 1.0, "Lluvioso": 0.78, "Nublado": 0.92}[clima]

        # Es festivo (simulado ~5% de los dias)
        es_festivo = 1 if rng.random() < 0.05 else 0

        for producto, info in PRODUCTOS.items():
            # Ventas base por producto (proporcional a su popularidad real)
            bases = {
                "Salchipapa": 18, "Hamburguesa": 22, "Perro Caliente": 15,
                "Pizza Personal": 14, "Empanada": 28, "Arepa Rellena": 20,
                "Limonada Natural": 16, "Gaseosa Personal": 22, "Porcion de Papas": 24
            }
            base = bases[producto]

            # Calcular unidades del dia
            ruido = 1 + rng.normal(0, 0.08)
            unidades = base * factor_trafico * factor_clima * ruido
            if es_festivo:
                unidades *= 1.25
            unidades = max(2, int(round(unidades)))

            # Calcular precio y margen
            precio = info["precio"]
            costo = info["costo"]
            margen = ((precio - costo) / precio) * 100
            ingreso = precio * unidades
            costo_total = costo * unidades

            registros.append({
                "fecha": fecha.strftime("%Y-%m-%d"),
                "dia_semana": dia_semana,
                "es_fin_semana": es_fin_semana,
                "es_festivo": es_festivo,
                "clima": clima,
                "producto": producto,
                "categoria": info["categoria"],
                "precio": precio,
                "costo": costo,
                "margen_pct": round(margen, 2),
                "unidades": unidades,
                "ingreso": ingreso,
                "costo_total": costo_total,
            })

    df = pd.DataFrame(registros)

    # Calcular precio promedio por categoria (feature adicional)
    cat_precios = df.groupby("categoria")["precio"].mean().to_dict()
    df["precio_prom_categoria"] = df["categoria"].map(cat_precios)

    # Crear target de clasificacion
    df["demanda_categoria"] = pd.cut(
        df["unidades"],
        bins=[0, 14, 29, float("inf")],
        labels=["BAJA", "MEDIA", "ALTA"]
    )

    return df


# =============================================================================
# 3. PREPROCESAMIENTO Y FEATURE ENGINEERING
# =============================================================================

def preparar_features(df):
    """Convierte el DataFrame en features numericas para los modelos."""
    X = df.copy()

    # Codificar dia de la semana
    le_dia = LabelEncoder()
    X["dia_semana_enc"] = le_dia.fit_transform(X["dia_semana"])

    # Codificar clima
    le_clima = LabelEncoder()
    X["clima_enc"] = le_clima.fit_transform(X["clima"])

    # Codificar categoria
    le_cat = LabelEncoder()
    X["categoria_enc"] = le_cat.fit_transform(X["categoria"])

    # Features finales
    features = [
        "precio", "costo", "margen_pct",
        "es_fin_semana", "es_festivo",
        "dia_semana_enc", "clima_enc", "categoria_enc",
        "precio_prom_categoria"
    ]

    X = X[features].copy()
    return X, {
        "le_dia": le_dia,
        "le_clima": le_clima,
        "le_cat": le_cat,
        "features": features
    }


# =============================================================================
# 4. ENTRENAMIENTO Y EVALUACION
# =============================================================================

def entrenar_modelos(df):
    """Entrena clasificador y regresor, evalua y retorna modelos + metricas."""
    print("=" * 60)
    print(" GASTRODATA - ENTRENAMIENTO DE MODELOS PREDICTIVOS")
    print("=" * 60)

    # Preparar features
    X, encoders = preparar_features(df)

    # Targets
    le_target = LabelEncoder()
    y_clf = le_target.fit_transform(df["demanda_categoria"])
    y_reg = df["unidades"]

    # Split estratificado para clasificacion
    X_train, X_test, y_clf_train, y_clf_test = train_test_split(
        X, y_clf, test_size=0.20, random_state=42, stratify=y_clf
    )

    # Mismo split para regresion
    _, _, y_reg_train, y_reg_test = train_test_split(
        X, y_reg, test_size=0.20, random_state=42, stratify=y_clf
    )

    # Escalar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # --- CLASIFICADOR (XGBoost) ---
    print("\n[1/2] Entrenando clasificador XGBoost...")
    clf = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="mlogloss",
        use_label_encoder=False
    )
    clf.fit(X_train_scaled, y_clf_train)

    y_clf_pred = clf.predict(X_test_scaled)
    accuracy = accuracy_score(y_clf_test, y_clf_pred)
    f1 = f1_score(y_clf_test, y_clf_pred, average="weighted")
    cm = confusion_matrix(y_clf_test, y_clf_pred)
    clf_report = classification_report(
        y_clf_test, y_clf_pred,
        target_names=le_target.classes_,
        output_dict=True
    )

    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    print(f"  Matriz de confusion:\n{cm}")

    # --- REGRESOR (XGBoost) ---
    print("\n[2/2] Entrenando regresor XGBoost...")
    reg = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    reg.fit(X_train_scaled, y_reg_train)

    y_reg_pred = reg.predict(X_test_scaled)
    r2 = r2_score(y_reg_test, y_reg_pred)
    mae = mean_absolute_error(y_reg_test, y_reg_pred)
    rmse = np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))

    print(f"  R2 Score:  {r2:.4f}")
    print(f"  MAE:       {mae:.2f} unidades")
    print(f"  RMSE:      {rmse:.2f} unidades")

    # Feature importance
    fi_clf = dict(zip(encoders["features"], clf.feature_importances_))
    fi_reg = dict(zip(encoders["features"], reg.feature_importances_))

    # Armar metricas (conversion a tipos nativos de Python para JSON)
    def to_native(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: to_native(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [to_native(v) for v in obj]
        return obj

    metricas = {
        "accuracy": to_native(round(accuracy, 4)),
        "f1_score": to_native(round(f1, 4)),
        "r2_score": to_native(round(r2, 4)),
        "mae": to_native(round(mae, 2)),
        "rmse": to_native(round(rmse, 2)),
        "fecha_entrenamiento": "2026-05-01",
        "modelo": "XGBoost",
        "total_registros": to_native(len(df)),
        "dias_entrenamiento": to_native(df["fecha"].nunique()),
        "features": encoders["features"],
        "feature_importance_clasificador": {k: to_native(round(v, 4)) for k, v in sorted(fi_clf.items(), key=lambda x: -x[1])},
        "feature_importance_regresor": {k: to_native(round(v, 4)) for k, v in sorted(fi_reg.items(), key=lambda x: -x[1])},
        "classification_report": clf_report,
        "matriz_confusion": to_native(cm),
        "labels_clasificacion": le_target.classes_.tolist()
    }

    print("\n" + "=" * 60)
    print(" RESUMEN DE METRICAS")
    print("=" * 60)
    print(f"  Accuracy:  {metricas['accuracy']}  (objetivo > 0.85)")
    print(f"  F1-Score:  {metricas['f1_score']}  (objetivo > 0.85)")
    print(f"  R2 Score:  {metricas['r2_score']}  (objetivo > 0.85)")
    print(f"  MAE:       {metricas['mae']} unidades")

    cumplimiento = all([
        metricas["accuracy"] > 0.85,
        metricas["f1_score"] > 0.85,
        metricas["r2_score"] > 0.85
    ])
    print(f"\n  {'CUMPLE' if cumplimiento else 'NO CUMPLE'} con los KPIs (> 0.85)")
    print("=" * 60)

    return {
        "clf": clf,
        "reg": reg,
        "scaler": scaler,
        "encoders": encoders,
        "le_target": le_target,
        "metricas": metricas
    }


# =============================================================================
# 5. GUARDAR Y CARGAR MODELOS
# =============================================================================

MODELOS_DIR = "modelos"

def guardar_modelos(modelos):
    """Guarda modelos, scaler, encoders y metricas a disco."""
    os.makedirs(MODELOS_DIR, exist_ok=True)

    joblib.dump(modelos["clf"], os.path.join(MODELOS_DIR, "clasificador_demanda.pkl"))
    joblib.dump(modelos["reg"], os.path.join(MODELOS_DIR, "regresor_demanda.pkl"))
    joblib.dump(modelos["scaler"], os.path.join(MODELOS_DIR, "scaler.pkl"))
    joblib.dump(modelos["encoders"], os.path.join(MODELOS_DIR, "encoders.pkl"))
    joblib.dump(modelos["le_target"], os.path.join(MODELOS_DIR, "le_target.pkl"))

    with open(os.path.join(MODELOS_DIR, "metricas_modelo.json"), "w", encoding="utf-8") as f:
        json.dump(modelos["metricas"], f, indent=2, ensure_ascii=False)

    print(f"\nModelos guardados en '{MODELOS_DIR}/'")


def cargar_modelos():
    """Carga modelos guardados desde disco."""
    modelos = {}
    modelos["clf"] = joblib.load(os.path.join(MODELOS_DIR, "clasificador_demanda.pkl"))
    modelos["reg"] = joblib.load(os.path.join(MODELOS_DIR, "regresor_demanda.pkl"))
    modelos["scaler"] = joblib.load(os.path.join(MODELOS_DIR, "scaler.pkl"))
    modelos["encoders"] = joblib.load(os.path.join(MODELOS_DIR, "encoders.pkl"))
    modelos["le_target"] = joblib.load(os.path.join(MODELOS_DIR, "le_target.pkl"))

    with open(os.path.join(MODELOS_DIR, "metricas_modelo.json"), "r", encoding="utf-8") as f:
        modelos["metricas"] = json.load(f)

    return modelos


# =============================================================================
# 6. PREDICCION PARA NUEVOS DATOS
# =============================================================================

def predecir_demanda(modelos, producto, dia_semana, clima, es_festivo=0):
    """
    Predice la demanda para un producto en un dia especifico.

    Parametros:
        modelos: dict con modelos cargados
        producto: nombre del producto (str)
        dia_semana: nombre del dia (str)
        clima: "Soleado", "Lluvioso" o "Nublado"
        es_festivo: 0 o 1

    Retorna:
        dict con prediccion de categoria, unidades, confianza
    """
    info = PRODUCTOS[producto]
    enc = modelos["encoders"]

    # Calcular precio promedio de la categoria
    cat_productos = [p for p, i in PRODUCTOS.items() if i["categoria"] == info["categoria"]]
    precio_prom = np.mean([PRODUCTOS[p]["precio"] for p in cat_productos])

    # Armar vector de features
    raw_features = pd.DataFrame([{
        "precio": info["precio"],
        "costo": info["costo"],
        "margen_pct": ((info["precio"] - info["costo"]) / info["precio"]) * 100,
        "es_fin_semana": 1 if dia_semana in ["Sabado", "Domingo"] else 0,
        "es_festivo": es_festivo,
        "dia_semana_enc": enc["le_dia"].transform([dia_semana])[0],
        "clima_enc": enc["le_clima"].transform([clima])[0],
        "categoria_enc": enc["le_cat"].transform([info["categoria"]])[0],
        "precio_prom_categoria": precio_prom
    }])

    # Escalar
    X_scaled = modelos["scaler"].transform(raw_features)

    # Predecir
    cat_pred_encoded = modelos["clf"].predict(X_scaled)[0]
    cat_pred = modelos["le_target"].inverse_transform([cat_pred_encoded])[0]
    cat_proba = modelos["clf"].predict_proba(X_scaled)[0]
    confianza = float(max(cat_proba) * 100)
    unidades_pred = float(modelos["reg"].predict(X_scaled)[0])

    return {
        "producto": producto,
        "categoria": cat_pred,
        "unidades_estimadas": round(unidades_pred, 1),
        "confianza_pct": round(confianza, 1)
    }


def predecir_semana(modelos, fecha_inicio=None):
    """
    Genera predicciones para los proximos 7 dias para todos los productos.

    Retorna:
        list de dicts con predicciones
    """
    if fecha_inicio is None:
        fecha_inicio = datetime.now()

    resultados = []
    climas_semana = np.random.choice(CLIMAS, size=7, p=[0.45, 0.30, 0.25])

    for i in range(7):
        fecha = fecha_inicio + timedelta(days=i)
        dia = DIAS_SEMANA[fecha.weekday()]
        clima = climas_semana[i]
        es_festivo = 1 if i == 5 else 0  # simular un festivo

        for producto in PRODUCTOS:
            pred = predecir_demanda(
                modelos, producto, dia, clima, es_festivo
            )
            pred["dia"] = dia
            pred["fecha"] = fecha.strftime("%Y-%m-%d")
            pred["clima"] = clima
            resultados.append(pred)

    return resultados


# =============================================================================
# 7. MAIN
# =============================================================================

if __name__ == "__main__":
    print("Generando datos sinteticos...")
    df = generar_datos_sinteticos(n_dias=180, seed=42)
    print(f"  {len(df):,} registros generados ({df['fecha'].nunique()} dias)")

    modelos = entrenar_modelos(df)
    guardar_modelos(modelos)

    print("\nProbando prediccion de ejemplo...")
    ejemplo = predecir_demanda(modelos, "Hamburguesa", "Sabado", "Soleado")
    print(f"  Producto: {ejemplo['producto']}")
    print(f"  Demanda:  {ejemplo['categoria']}")
    print(f"  Unidades: {ejemplo['unidades_estimadas']}")
    print(f"  Confianza: {ejemplo['confianza_pct']}%")

    print("\nTodo listo. Los modelos estan entrenados y guardados.")
