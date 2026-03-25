@extends('admin.layout')

@section('content')
    <div class="header">
        <h1>Gestión de Equipos</h1>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3 class="mb-4">Crear Nuevo Equipo</h3>
            <form action="{{ route('admin.teams.store') }}" method="POST">
                @csrf
                <div class="form-group">
                    <label>Nombre del Equipo</label>
                    <input type="text" name="name" required placeholder="Ej. Soporte Nivel 1">
                </div>
                <button type="submit" class="btn btn-primary">Guardar Equipo</button>
            </form>
        </div>

        <div class="card table-container" style="margin-top: 0">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th style="text-align: right;">Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($teams as $team)
                    <tr>
                        <td>{{ $team->id }}</td>
                        <td style="font-weight: 500;">{{ $team->name }}</td>
                        <td style="text-align: right;">
                            <form action="{{ route('admin.teams.destroy', $team) }}" method="POST" onsubmit="return confirm('¿Eliminar este equipo?');">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-danger" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Eliminar</button>
                            </form>
                        </td>
                    </tr>
                    @endforeach
                    @if($teams->isEmpty())
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No hay equipos</td></tr>
                    @endif
                </tbody>
            </table>
        </div>
    </div>
@endsection
