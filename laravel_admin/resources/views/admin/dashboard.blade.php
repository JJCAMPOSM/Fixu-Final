@extends('admin.layout')

@section('content')
<!-- Include Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<div class="header" style="margin-bottom: 1.5rem;">
    <h1>Dashboard Analítico</h1>
</div>

<form method="GET" action="{{ route('admin.dashboard') }}" class="card" style="display: flex; gap: 1rem; align-items: flex-end; margin-bottom: 2rem; flex-wrap: wrap;">
    <div style="flex: 1; min-width: 150px;">
        <label for="start_date" style="display: block; font-weight: 500; margin-bottom: 0.5rem; color: var(--text-muted)">Fecha Inicio</label>
        <input type="date" id="start_date" name="start_date" class="form-control" value="{{ $start_date }}" required>
    </div>
    <div style="flex: 1; min-width: 150px;">
        <label for="end_date" style="display: block; font-weight: 500; margin-bottom: 0.5rem; color: var(--text-muted)">Fecha Fin</label>
        <input type="date" id="end_date" name="end_date" class="form-control" value="{{ $end_date }}" required>
    </div>
    <div style="display: flex; gap: 1rem; flex-wrap: nowrap; margin-top: auto;">
        <button type="submit" class="btn btn-primary" style="height: 42px; white-space: nowrap;">Filtrar</button>
        <a href="{{ route('admin.tickets.export.closed.pdf', ['start_date' => $start_date, 'end_date' => $end_date]) }}" target="_blank" class="btn btn-primary" style="height: 42px; display: inline-flex; align-items: center; background-color: #ef4444; border-color: #dc2626; white-space: nowrap;">Exportar PDF</a>
    </div>
</form>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
    <!-- Chart Agentes -->
    <div class="card" style="padding: 1.5rem;">
        <h3 style="margin-bottom: 1rem; color: var(--text-main); font-size: 1.1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">Tickets Resueltos por Agente</h3>
        <div style="height: 250px; width: 100%;">
            <canvas id="agentChart"></canvas>
        </div>
    </div>

    <!-- Chart Equipos -->
    <div class="card" style="padding: 1.5rem;">
        <h3 style="margin-bottom: 1rem; color: var(--text-main); font-size: 1.1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">Tickets Resueltos por Equipo</h3>
        <div style="height: 250px; width: 100%;">
            <canvas id="teamChart"></canvas>
        </div>
    </div>

    <!-- Chart Categorías -->
    <div class="card" style="padding: 1.5rem;">
        <h3 style="margin-bottom: 1rem; color: var(--text-main); font-size: 1.1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">Tickets Resueltos por Categoría</h3>
        <div style="height: 250px; width: 100%;">
            <canvas id="categoryChart"></canvas>
        </div>
    </div>
</div>

<script>
    // Configuración global para Chart.js respetando el dark theme
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Inter', sans-serif";
    
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                titleColor: '#fff',
                bodyColor: '#fff',
                padding: 10,
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: { stepSize: 1 },
                grid: { color: 'rgba(255, 255, 255, 0.05)' }
            },
            x: {
                grid: { display: false }
            }
        }
    };

    // Datos desde PHP a JS
    const agentData = @json($ticketsByAgent);
    const teamData = @json($ticketsByTeam);
    const categoryData = @json($ticketsByCategory);

    // Helper para inicializar charts de barras
    function createBarChart(elementId, dataObj, colorBase) {
        if(Object.keys(dataObj).length === 0) {
            dataObj = {'Sin Datos': 0};
        }
        new Chart(document.getElementById(elementId), {
            type: 'bar',
            data: {
                labels: Object.keys(dataObj),
                datasets: [{
                    data: Object.values(dataObj),
                    backgroundColor: `rgba(${colorBase}, 0.8)`,
                    borderColor: `rgba(${colorBase}, 1)`,
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: commonOptions
        });
    }

    // Dibujar gráficas de barras con paleta temática
    document.addEventListener("DOMContentLoaded", function() {
        createBarChart('agentChart', agentData, '99, 102, 241'); // Indigo/Primary
        createBarChart('teamChart', teamData, '16, 185, 129'); // Emerald/Success
        createBarChart('categoryChart', categoryData, '239, 68, 68'); // Red/Danger
    });
</script>
@endsection
