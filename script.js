/**
 * GastroData - Script de Inteligencia de Negocio
 * Arquitectura Medallón Simulada en Frontend
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. DATASET SIMULADO (Capa Bronce: Datos Crudos)
    const rawSalesData = generateRawData(30); 

    // 2. PROCESAMIENTO (Capa Plata: Limpieza y Agregación)
    const silverData = processToSilver(rawSalesData);

    // 3. MÉTRICAS DE NEGOCIO (Capa Oro: KPIs y Predicciones)
    const goldMetrics = generateGoldMetrics(silverData);

    // 4. INFERENCIA (Modelo Predictivo Simple)
    const projections = runPredictiveModel(silverData, 7);

    // variables de simulación globales
    window.currentRaw = rawSalesData;
    window.currentSilver = silverData;
    window.currentGold = goldMetrics;
    window.currentProj = projections;

    // 5. RENDERIZACIÓN INICIAL CON RETRASO SEGURO
    setTimeout(() => {
        renderDashboard(window.currentSilver, window.currentProj, window.currentGold, window.currentRaw);
    }, 500);

    // Inyectar Alertas (Categorías Expandidas con Horas Pico)
    const alertsContainer = document.getElementById('alerts-container');
    const peakHour = Math.floor(Math.random() * 3) + 18; // Simulación de pico entre 6pm y 9pm
    const alerts = [
        { type: 'warning', text: `Ajuste de Stock: Se prevé lluvia el fin de semana. Reducir insumos perecederos un 15%.` },
        { type: 'success', text: `Oportunidad: Alta demanda de ${goldMetrics.topDish} detectada para el festivo.` },
        { type: 'info', text: `🕒 Operativo: Pico de demanda esperado a las ${peakHour}:00 PM. Iniciar pre-alistamiento de ${goldMetrics.topDish} 30 min antes.` }
    ];

    if (alertsContainer) {
        alertsContainer.innerHTML = alerts.map(a => `<div class="alert alert-${a.type}">${a.text}</div>`).join('');
    }

    // Event Listeners para Simulador
    const trafficSlider = document.getElementById('sim-traffic');
    const priceSlider = document.getElementById('sim-price');

    const updateSimulation = () => {
        const trafficMult = trafficSlider.value / 100;
        const priceMult = 1 + (priceSlider.value / 100);
        
        document.getElementById('val-traffic').innerText = trafficSlider.value;
        document.getElementById('val-price').innerText = priceSlider.value;

        // Aplicar simulación a los datos de Oro
        const simulatedGold = {
            ...goldMetrics,
            totalRevenue: goldMetrics.totalRevenue * trafficMult * priceMult,
            avgMargin: (parseFloat(goldMetrics.avgMargin) * priceMult).toFixed(1)
        };

        // Aplicar simulación a Proyecciones
        const simulatedProj = projections.map(p => ({
            ...p,
            projectedRevenue: p.projectedRevenue * trafficMult * priceMult
        }));

        renderDashboard(silverData, simulatedProj, simulatedGold, rawSalesData);
    };

    if (trafficSlider) trafficSlider.addEventListener('input', updateSimulation);
    if (priceSlider) priceSlider.addEventListener('input', updateSimulation);

    // Sync Button
    const syncBtn = document.getElementById('refresh-data');
    if (syncBtn) {
        syncBtn.addEventListener('click', () => {
            syncBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            setTimeout(() => location.reload(), 1000);
        });
    }

    // Download Report Button (Historial Detallado)
    const downloadBtn = document.getElementById('download-report');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            let csv = 'ID_Transaccion,Fecha_Hora,Producto,Mesa,Metodo_Pago,Precio_Venta,Costo_Insumo,Utilidad\n';
            window.currentRaw.forEach(r => {
                const utilidad = r.price - r.cost;
                csv += `${r.id},${r.timestamp.replace('T', ' ').substr(0, 19)},${r.item},${r.table},${r.paymentMethod},${r.price},${r.cost.toFixed(0)},${utilidad.toFixed(0)}\n`;
            });
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.setAttribute('hidden', '');
            a.setAttribute('href', url);
            a.setAttribute('download', 'historial_ventas_detallado.csv');
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    }

    // Navegación
    const navAbout = document.getElementById('nav-about');
    const methodSection = document.getElementById('methodology-section');
    if (navAbout) {
        navAbout.addEventListener('click', () => {
            const isHidden = methodSection.style.display === 'none';
            methodSection.style.display = isHidden ? 'block' : 'none';
            if (isHidden) methodSection.scrollIntoView({ behavior: 'smooth' });
        });
    }
});

/**
 * Genera datos crudos (Bronce)
 */
function generateRawData(days) {
    const data = [];
    const dishes = ['Salchipapa', 'Hamburguesa', 'Perro Caliente', 'Pizza Personal', 'Empanada', 'Arepa Rellena', 'Limonada Natural', 'Gaseosa Personal', 'Porción de Papas'];
    const now = new Date();
    for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(now.getDate() - i);
        const isWeekend = date.getDay() === 0 || date.getDay() === 6;
        const baseSales = isWeekend ? 120 : 70;
        const totalSales = baseSales + Math.floor(Math.random() * 30);
        for (let j = 0; j < totalSales; j++) {
            const dish = dishes[Math.floor(Math.random() * dishes.length)];
            const price = dish.includes('Hamburguesa') ? 22000 : 
                          dish.includes('Salchipapa') ? 18000 : 
                          dish.includes('Pizza') ? 25000 : 
                          dish.includes('Perro') ? 15000 : 
                          dish.includes('Empanada') ? 3500 : 
                          dish.includes('Arepa') ? 12000 : 
                          dish.includes('Limonada') ? 8000 :
                          dish.includes('Gaseosa') ? 5000 : 7000;
            const paymentMethods = ['Efectivo', 'Tarjeta', 'Transferencia'];
            data.push({ 
                id: `TX-${Math.random().toString(36).substr(2, 5).toUpperCase()}`,
                timestamp: date.toISOString(), 
                item: dish, 
                price: price, 
                cost: price * 0.45, 
                paymentMethod: paymentMethods[Math.floor(Math.random() * paymentMethods.length)],
                table: Math.floor(Math.random() * 20) + 1 
            });
        }
    }
    return data;
}

function processToSilver(rawData) {
    const dailyMap = {};
    const itemMap = {};
    rawData.forEach(record => {
        const date = record.timestamp.split('T')[0];
        if (!dailyMap[date]) dailyMap[date] = { date, revenue: 0, profit: 0, count: 0 };
        dailyMap[date].revenue += record.price;
        dailyMap[date].profit += (record.price - record.cost);
        dailyMap[date].count++;
        if (!itemMap[record.item]) itemMap[record.item] = { name: record.item, count: 0, revenue: 0 };
        itemMap[record.item].count++;
        itemMap[record.item].revenue += record.price;
    });
    return {
        daily: Object.values(dailyMap).sort((a, b) => new Date(a.date) - new Date(b.date)),
        items: Object.values(itemMap).sort((a, b) => b.revenue - a.revenue)
    };
}

function generateGoldMetrics(silverData) {
    const totalRevenue = silverData.daily.reduce((sum, d) => sum + d.revenue, 0);
    const totalProfit = silverData.daily.reduce((sum, d) => sum + d.profit, 0);
    return { totalRevenue, avgMargin: ((totalProfit / totalRevenue) * 100).toFixed(1), topDish: silverData.items[0].name };
}

function runPredictiveModel(silverData, forecastDays) {
    const last14Days = silverData.daily.slice(-14);
    const lastDate = new Date(silverData.daily[silverData.daily.length - 1].date);
    const weatherForecast = ['Soleado', 'Lluvioso', 'Nublado', 'Soleado', 'Soleado', 'Lluvioso', 'Soleado'];
    const projections = [];
    for (let i = 1; i <= forecastDays; i++) {
        const projDate = new Date(lastDate);
        projDate.setDate(lastDate.getDate() + i);
        const dayOfWeek = projDate.getDay();
        const sameDayLastWeek = last14Days.find(d => new Date(d.date).getDay() === dayOfWeek);
        let baseRevenue = sameDayLastWeek ? sameDayLastWeek.revenue : 850000;
        const multiplier = (dayOfWeek === 0 || dayOfWeek === 6) ? 1.35 : 1.0;
        const weatherImpact = weatherForecast[i-1] === 'Lluvioso' ? 0.85 : 1.1;
        projections.push({ date: projDate.toISOString().split('T')[0], projectedRevenue: baseRevenue * multiplier * weatherImpact, weather: weatherForecast[i-1], isHoliday: i === 5 });
    }
    return projections;
}

function renderDashboard(silver, projections, gold, raw) {
    document.getElementById('kpi-sales').innerText = `$${(gold.totalRevenue / 1000000).toFixed(1)}M COP`;
    document.getElementById('kpi-margin').innerText = `${gold.avgMargin}%`;
    
    const feedContainer = document.getElementById('live-feed');
    if (feedContainer) {
        feedContainer.innerHTML = raw.slice(-15).reverse().map(r => `
            <div class="feed-item">
                <span class="timestamp">[${r.timestamp.split('T')[1].split('.')[0]}]</span>
                <span class="event">${r.item} - Table ${r.table}</span>
            </div>
        `).join('');
    }

    const predTable = document.getElementById('predictions-table');
    if (predTable) {
        predTable.innerHTML = silver.items.slice(0, 3).map(item => `
            <div class="pred-item">
                <span class="pred-name">${item.name}</span>
                <span class="pred-value">${Math.floor(item.count * 1.1)} un.</span>
            </div>
        `).join('');
    }

    // CHARTS
    const salesCanvas = document.getElementById('salesChart');
    if (salesCanvas) {
        const ctx = salesCanvas.getContext('2d');
        const labels = [...silver.daily.map(d => d.date.split('-')[1]+'/'+d.date.split('-')[2]), ...projections.map(p => p.date.split('-')[1]+'/'+p.date.split('-')[2])];
        const hist = [...silver.daily.map(d => d.revenue), ...new Array(projections.length).fill(null)];
        const proj = [...new Array(silver.daily.length - 1).fill(null), silver.daily[silver.daily.length-1].revenue, ...projections.map(p => p.projectedRevenue)];
        
        if (window.myChart1) window.myChart1.destroy();
        window.myChart1 = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    { label: 'Histórico', data: hist, borderColor: '#0284c7', backgroundColor: 'rgba(2,132,199,0.1)', fill: true, tension: 0.4 },
                    { label: 'Proyectado', data: proj, borderColor: '#059669', borderDash: [5,5], tension: 0.4 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } } } }
        });
    }

    const popCanvas = document.getElementById('popularityChart');
    if (popCanvas) {
        const ctx = popCanvas.getContext('2d');
        if (window.myChart2) window.myChart2.destroy();
        window.myChart2 = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: silver.items.map(i => i.name),
                datasets: [{ data: silver.items.map(i => i.count), backgroundColor: ['#0284c7', '#0ea5e9', '#059669', '#10b981', '#34d399'] }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}
