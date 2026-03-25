@extends('admin.layout')

@section('content')
    <div class="header">
        <h1>Gestión de Solicitantes</h1>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3 class="mb-4">Agregar Solicitante</h3>
            <form action="{{ route('admin.requesters.store') }}" method="POST">
                @csrf
                <div class="form-group">
                    <label>Nombre</label>
                    <input type="text" name="name" required placeholder="Ej. Juan Pérez">
                </div>
                <div class="form-group">
                    <label>Correo Electrónico</label>
                    <input type="email" name="email" required placeholder="juan@ejemplo.com">
                </div>
                <div class="form-group">
                    <label>Teléfono</label>
                    <input type="text" name="phone" placeholder="Ej. +52 555 123 4567">
                </div>
                <button type="submit" class="btn btn-primary">Guardar Solicitante</button>
            </form>
        </div>

        <div class="card table-container" style="margin-top: 0">
            <table>
                <thead>
                    <tr>
                        <th>Nombre</th>
                        <th>Contacto</th>
                        <th style="text-align: right;">Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($requesters as $requester)
                    <tr>
                        <td style="font-weight: 500;">
                            {{ $requester->name }}
                        </td>
                        <td>
                            <div style="color: var(--text-main);">{{ $requester->email }}</div>
                            <div style="font-size: 0.8rem; color: var(--text-muted);">{{ $requester->phone }}</div>
                        </td>
                        <td style="text-align: right;">
                            <form action="{{ route('admin.requesters.destroy', $requester) }}" method="POST" onsubmit="return confirm('¿Eliminar solicitante?');">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-danger" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Eliminar</button>
                            </form>
                        </td>
                    </tr>
                    @endforeach
                    @if($requesters->isEmpty())
                        <tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No hay solicitantes registrados</td></tr>
                    @endif
                </tbody>
            </table>
        </div>
    </div>
@endsection
