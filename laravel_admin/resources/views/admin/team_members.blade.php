@extends('admin.layout')

@section('content')
    <div class="header">
        <h1>Miembros: {{ $team->name }}</h1>
        <a href="{{ route('admin.teams.index') }}" class="btn" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white;">&larr; Volver a Equipos</a>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3 class="mb-4">Asignar Agente</h3>
            <form action="{{ route('admin.teams.members.add', $team) }}" method="POST">
                @csrf
                <div class="form-group">
                    <label>Seleccionar Agente</label>
                    <select name="user_id" required>
                        <option value="">-- Seleccione un agente --</option>
                        @foreach($available_agents as $agent)
                            <option value="{{ $agent->id }}">{{ $agent->name }} ({{ $agent->email }})</option>
                        @endforeach
                    </select>
                </div>
                <button type="submit" class="btn btn-primary">Añadir al Equipo</button>
            </form>
        </div>

        <div class="card table-container" style="margin-top: 0">
            <table>
                <thead>
                    <tr>
                        <th>Agente asignado</th>
                        <th style="text-align: right;">Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($members as $member)
                    <tr>
                        <td style="font-weight: 500;">
                            {{ $member->user->name }}
                            <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: normal;">{{ $member->user->email }}</div>
                        </td>
                        <td style="text-align: right;">
                            <form action="{{ route('admin.team-members.remove', $member) }}" method="POST" onsubmit="return confirm('¿Remover a este agente del equipo?');">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-danger" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Remover</button>
                            </form>
                        </td>
                    </tr>
                    @endforeach
                    @if($members->isEmpty())
                        <tr><td colspan="2" style="text-align: center; color: var(--text-muted);">El equipo no tiene miembros asignados</td></tr>
                    @endif
                </tbody>
            </table>
        </div>
    </div>
@endsection
