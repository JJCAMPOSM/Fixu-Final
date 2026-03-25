@extends('admin.layout')

@section('content')
    <div class="header">
        <h1>Gestión de Agentes</h1>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3 class="mb-4">Registrar Agente</h3>
            <form action="{{ route('admin.agents.store') }}" method="POST">
                @csrf
                <div class="form-group">
                    <label>Nombre</label>
                    <input type="text" name="name" required placeholder="Nombre completo">
                </div>
                <div class="form-group">
                    <label>Correo Electrónico (Login)</label>
                    <input type="email" name="email" required placeholder="agente@fixu.local">
                </div>
                <div class="form-group">
                    <label>Contraseña</label>
                    <input type="password" name="password" required placeholder="Mínimo 6 caracteres">
                </div>
                <button type="submit" class="btn btn-primary">Registrar Agente</button>
            </form>
        </div>

        <div class="card table-container" style="margin-top: 0">
            <table>
                <thead>
                    <tr>
                        <th>Agente</th>
                        <th>Rol</th>
                        <th style="text-align: right;">Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($agents as $agent)
                    <tr>
                        <td style="font-weight: 500;">
                            {{ $agent->name }}
                            <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: normal;">{{ $agent->email }}</div>
                        </td>
                        <td>
                            <span style="background: rgba(99, 102, 241, 0.2); color: var(--primary); padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: 500; text-transform: uppercase;">{{ $agent->role }}</span>
                        </td>
                        <td style="text-align: right;">
                            <form action="{{ route('admin.agents.destroy', $agent) }}" method="POST" onsubmit="return confirm('¿Dar de baja a este agente?');">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-danger" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Eliminar</button>
                            </form>
                        </td>
                    </tr>
                    @endforeach
                    @if($agents->isEmpty())
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No hay agentes registrados</td></tr>
                    @endif
                </tbody>
            </table>
        </div>
    </div>
@endsection
