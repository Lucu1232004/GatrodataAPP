import os
from weasyprint import HTML

# Contenido del informe basado en la entrada del usuario
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 20mm;
            background-color: #ffffff;
            @bottom-right {
                content: counter(page);
                font-size: 9pt;
                color: #666;
            }
        }
        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #333;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        .header-banner {
            background-color: #1a3a5a;
            color: white;
            padding: 30px;
            margin: -20mm -20mm 20mm -20mm;
            text-align: left;
        }
        .header-banner h1 {
            margin: 0;
            font-size: 22pt;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .header-banner p {
            margin: 5px 0 0 0;
            font-size: 11pt;
            opacity: 0.9;
        }
        .section-title {
            color: #1a3a5a;
            border-bottom: 2px solid #1a3a5a;
            padding-bottom: 5px;
            margin-top: 25px;
            font-size: 14pt;
            text-transform: uppercase;
        }
        .subsection-title {
            color: #2c5f91;
            font-size: 12pt;
            margin-top: 15px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .content-block {
            margin-bottom: 15px;
            text-align: justify;
        }
        .highlight-box {
            background-color: #f0f4f8;
            border-left: 5px solid #1a3a5a;
            padding: 15px;
            margin: 20px 0;
        }
        .metric-grid {
            display: block;
            margin: 15px 0;
        }
        .metric-item {
            background-color: #ffffff;
            border: 1px solid #d1d9e0;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .footer-brand {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            font-style: italic;
            color: #777;
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin-bottom: 8px;
        }
        .tagline {
            font-weight: bold;
            color: #1a3a5a;
        }
    </style>
</head>
<body>
    <div class="header-banner">
        <h1>Informe Técnico: Prototipo Alpha GastroData</h1>
        <p>Sistema de Inteligencia de Negocio y Analítica Predictiva</p>
        <p><strong>Fecha:</strong> 20 de Abril de 2026 | <strong>Autor:</strong> Samuel Admin</p>
    </div>

    <h2 class="section-title">1. Resumen Ejecutivo</h2>
    <div class="content-block">
        GastroData es una plataforma de analítica avanzada diseñada para optimizar la eficiencia operativa y financiera en el sector gastronómico. El prototipo Alpha implementa un ecosistema de datos basado en la <strong>Arquitectura Medallón</strong>, permitiendo la transición de datos transaccionales en bruto hacia inferencias predictivas que reducen el desperdicio de inventario y optimizan el flujo de caja.
    </div>

    <h2 class="section-title">2. Metodología de Diseño (Data Thinking)</h2>
    <div class="content-block">
        El desarrollo se fundamentó en el proceso de <strong>Data Thinking</strong>, priorizando las necesidades del usuario final (gerentes de restaurantes).
    </div>

    <h3 class="subsection-title">2.1 Proceso de Jerarquía Analítica (AHP)</h3>
    <div class="content-block">
        Para determinar el alcance funcional, se aplicó la técnica AHP, evaluando la viabilidad y el retorno de inversión. El <strong>Sistema de Gestión Inteligente</strong> fue seleccionado como el núcleo del prototipo.
    </div>
    <ul>
        <li><strong>Impacto en el ROI (45%):</strong> Prioridad alta por ahorro en costos operativos.</li>
        <li><strong>Factibilidad Técnica (30%):</strong> Implementación viable mediante infraestructura de datos moderna.</li>
        <li><strong>Experiencia del Usuario (25%):</strong> Enfoque en dashboards intuitivos.</li>
    </ul>

    <h2 class="section-title">3. Arquitectura Técnica (Medallion)</h2>
    <div class="content-block">
        Se implementó un pipeline de datos robusto estructurado en tres capas críticas:
    </div>
    <ul>
        <li><strong>Capa Bronce (Raw):</strong> Ingesta continua de micro-transacciones (producto, ID de venta, mesa y método de pago).</li>
        <li><strong>Capa Plata (Silver):</strong> Limpieza, eliminación de duplicados y estandarización. Se calculan márgenes operativos integrando costos de insumos.</li>
        <li><strong>Capa Oro (Gold):</strong> Datos agregados para visualización. KPIs críticos de ingresos y tendencias para el Dashboard ejecutivo.</li>
    </ul>

    <h2 class="section-title">4. Modelo Predictivo e Inferencia</h2>
    <div class="content-block">
        El motor utiliza un modelo de ensamble basado en <strong>Random Forest</strong> para generar proyecciones de demanda a 7 días, integrando histórico de ventas, factores ambientales y calendario.
    </div>

    <div class="highlight-box">
        <strong>Salud del Modelo:</strong>
        <p>El prototipo reporta un <strong>R² de 0.89</strong> y un MAE (Error Medio Absoluto) controlado, garantizando que el 89% de la varianza en las ventas es explicada por las variables del modelo.</p>
    </div>

    <h2 class="section-title">5. Simulador de Escenarios Reactivo</h2>
    <div class="content-block">
        El simulador de negocio permite realizar análisis de sensibilidad sobre variables críticas:
    </div>
    <ul>
        <li><strong>Tráfico de Clientes:</strong> Evaluación de capacidad instalada.</li>
        <li><strong>Elasticidad de Precios:</strong> Impacto en márgenes por cambios en el menú.</li>
        <li><strong>Eficiencia Operativa:</strong> Proyección de pérdidas por desperdicio.</li>
    </ul>

    <h2 class="section-title">6. Conclusiones y Recomendaciones</h2>
    <div class="content-block">
        1. <strong>Reducción de Riesgos:</strong> La inferencia de "Horas Pico" optimiza la planeación de personal.<br>
        2. <strong>Transparencia Financiera:</strong> Facilidad en auditoría contable y reporte de utilidad neta.<br>
        3. <strong>Escalabilidad:</strong> Preparado para integración con APIs de proveedores para automatizar compras.
    </div>

    <div class="footer-brand">
        <p class="tagline">GastroData Intelligence</p>
        <p>Transformando la Gastronomía a través de la Ciencia de Datos</p>
    </div>
</body>
</html>
"""

# Guardar HTML temporal y convertir a PDF
output_html = "informe_gastrodata.html"
output_pdf = "informe_tecnico_gastrodata_alpha.pdf"

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generando PDF: {output_pdf}...")
try:
    HTML(string=html_content).write_pdf(output_pdf)
    print("¡Informe generado exitosamente!")
except Exception as e:
    print(f"Error al generar el PDF: {e}")
