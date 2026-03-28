<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte KPI de Tickets Resueltos</title>
    <style>
        body { font-family: 'Helvetica', 'Arial', sans-serif; font-size: 12px; color: #333; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #ef4444; padding-bottom: 10px; }
        .header h1 { margin: 0; color: #b91c1c; font-size: 22px; text-transform: uppercase; letter-spacing: 1px; }
        .header p { margin: 5px 0; color: #6b7280; font-size: 13px; font-weight: bold; }
        .stats { margin-bottom: 15px; font-weight: bold; font-size: 14px; display: inline-block; padding: 8px 12px; background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 4px; color: #991b1b; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: left; }
        th { background-color: #f9fafb; color: #374151; font-weight: bold; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
        tr:nth-child(even) { background-color: #f9fafb; }
        .status-solved { color: #059669; font-weight: bold; font-size: 11px; text-transform: uppercase; }
        .status-closed { color: #4b5563; font-weight: bold; font-size: 11px; text-transform: uppercase; }
        .footer { position: fixed; bottom: -30px; left: 0px; right: 0px; height: 30px; text-align: right; font-size: 10px; color: #9ca3af; border-top: 1px solid #e5e7eb; padding-top: 5px; }
        .page-number:after { content: counter(page); }
    </style>
</head>
<body>
    <div class="footer">
        Generado el {{ now()->format('d/m/Y H:i') }} - Fixu Helpdesk - Página <span class="page-number"></span>
    </div>

    <div class="header">
        <h1>Reporte de Productividad y CIERRE DE TICKETS</h1>
        <p>PERIODO DE EVALUACIÓN: {{ \Carbon\Carbon::parse($startDate)->format('d/m/Y') }} AL {{ \Carbon\Carbon::parse($endDate)->format('d/m/Y') }}</p>
    </div>

    <div class="stats">
        Total de Tickets Finalizados en este periodo: {{ $tickets->count() }}
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 5%">ID</th>
                <th style="width: 25%">Título del Ticket</th>
                <th style="width: 15%">Categoría</th>
                <th style="width: 15%">Solicitante</th>
                <th style="width: 15%">Cerrado Por (Agente)</th>
                <th style="width: 10%">Estado Final</th>
                <th style="width: 15%">Fecha de Cierre</th>
            </tr>
        </thead>
        <tbody>
            @forelse($tickets as $ticket)
            <tr>
                <td><strong>#{{ $ticket->id }}</strong></td>
                <td>{{ $ticket->title }}</td>
                <td>{{ $ticket->category ? $ticket->category->name : 'No Asignada' }}</td>
                <td>{{ $ticket->requester->name ?? 'N/A' }}</td>
                <td>{{ $ticket->assignee && $ticket->assignee->user ? $ticket->assignee->user->name : 'N/A' }}</td>
                <td class="{{ $ticket->status == 'solved' ? 'status-solved' : 'status-closed' }}">
                    {{ $ticket->status == 'solved' ? 'Resuelto' : 'Cerrado' }}
                </td>
                <td>{{ \Carbon\Carbon::parse($ticket->updated_at)->format('d/m/Y H:i') }}</td>
            </tr>
            @empty
            <tr>
                <td colspan="7" style="text-align: center; padding: 30px; font-style: italic; color: #6b7280;">
                    No existen tickets cerrados o resueltos para el filtro de fechas seleccionado.
                </td>
            </tr>
            @endforelse
        </tbody>
    </table>
</body>
</html>
