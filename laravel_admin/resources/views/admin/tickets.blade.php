@extends('admin.layout')

@section('content')
    <div class="header">
        <h1>Gestión de Tickets</h1>
        <div class="flex gap-4">
            <a href="{{ route('admin.tickets.export.excel') }}" class="btn" style="background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2);">Exportar Excel</a>
            <a href="{{ route('admin.tickets.export.pdf') }}" class="btn" style="background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2);">Exportar PDF</a>
        </div>
    </div>

    <div class="card table-container">
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Título</th>
                    <th>Estado</th>
                    <th>Prioridad</th>
                    <th>Solicitante</th>
                    <th>Asignado</th>
                    <th style="text-align: right;">Acciones</th>
                </tr>
            </thead>
            <tbody>
                @foreach($tickets as $ticket)
                <tr>
                    <td>#{{ $ticket->id }}</td>
                    <td style="font-weight: 500;">
                        {{ \Illuminate\Support\Str::limit($ticket->title, 40) }}
                        <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: normal;">
                            {{ $ticket->created_at->format('Y-m-d H:i') }}
                        </div>
                    </td>
                    <td>
                        @php
                            $statusColors = [
                                'open' => '#10b981', 
                                'pending' => '#f59e0b', 
                                'solved' => '#6366f1', 
                                'closed' => '#64748b'
                            ];
                        @endphp
                        <span style="background: {{ $statusColors[$ticket->status] ?? '#64748b' }}22; color: {{ $statusColors[$ticket->status] ?? '#64748b' }}; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 500; text-transform: uppercase;">
                            {{ $ticket->status }}
                        </span>
                    </td>
                    <td>
                        @php
                            $priorityColors = [
                                'low' => '#64748b', 
                                'medium' => '#f59e0b', 
                                'high' => '#ef4444'
                            ];
                        @endphp
                         <span style="background: {{ $priorityColors[$ticket->priority] ?? '#64748b' }}22; color: {{ $priorityColors[$ticket->priority] ?? '#64748b' }}; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 500; text-transform: uppercase;">
                            {{ $ticket->priority }}
                        </span>
                    </td>
                    <td>{{ $ticket->requester ? $ticket->requester->name : 'N/A' }}</td>
                    <td>{{ $ticket->assignee && $ticket->assignee->user ? $ticket->assignee->user->name : 'N/A' }}</td>
                    <td style="text-align: right;">
                        <a href="{{ route('admin.tickets.edit', $ticket) }}" class="btn" style="background: rgba(99, 102, 241, 0.1); color: var(--primary); border: 1px solid rgba(99, 102, 241, 0.2); padding: 0.3rem 0.6rem; font-size: 0.85rem;">Editar</a>
                    </td>
                </tr>
                @endforeach
                @if($tickets->isEmpty())
                    <tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No hay tickets creados</td></tr>
                @endif
            </tbody>
        </table>
    </div>
@endsection
