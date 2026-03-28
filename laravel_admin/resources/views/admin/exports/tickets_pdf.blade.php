<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reporte de Tickets</title>
    <style>
        body { font-family: 'Helvetica', sans-serif; font-size: 10pt; color: #333; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #6366f1; padding-bottom: 10px; }
        .date { text-align: right; font-size: 8pt; color: #666; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background-color: #f3f4f6; color: #374151; font-weight: bold; text-align: left; padding: 8px; border: 1px solid #d1d5db; }
        td { padding: 8px; border: 1px solid #d1d5db; vertical-align: top; }
        .status { text-transform: uppercase; font-weight: bold; font-size: 8pt; }
        .priority-high { color: #ef4444; }
        .priority-medium { color: #f59e0b; }
        .priority-low { color: #6b7280; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Reporte de Tickets - Fixu Admin</h1>
        <div class="date">Generado el: {{ now()->format('d/m/Y H:i') }}</div>
    </div>

    <table>
        <thead>
            <tr>
                <th width="5%">ID</th>
                <th width="25%">Título</th>
                <th width="10%">Estado</th>
                <th width="10%">Prioridad</th>
                <th width="15%">Solicitante</th>
                <th width="15%">Equipo</th>
                <th width="20%">Asignado</th>
            </tr>
        </thead>
        <tbody>
            @php
                $statusLabels = ['open' => 'Abierto', 'pending' => 'Pendiente', 'solved' => 'Resuelto', 'closed' => 'Cerrado'];
                $priorityLabels = ['low' => 'Baja', 'medium' => 'Media', 'high' => 'Alta'];
            @endphp
            @foreach($tickets as $ticket)
            <tr>
                <td>#{{ $ticket->id }}</td>
                <td>{{ $ticket->title }}</td>
                <td class="status">{{ $statusLabels[$ticket->status] ?? $ticket->status }}</td>
                <td class="status priority-{{ $ticket->priority }}">{{ $priorityLabels[$ticket->priority] ?? $ticket->priority }}</td>
                <td>{{ $ticket->requester ? $ticket->requester->name : 'N/A' }}</td>
                <td>{{ $ticket->team ? $ticket->team->name : 'N/A' }}</td>
                <td>{{ ($ticket->assignee && $ticket->assignee->user) ? $ticket->assignee->user->name : 'N/A' }}</td>
            </tr>
            @endforeach
        </tbody>
    </table>
</body>
</html>
