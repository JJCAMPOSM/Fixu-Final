@extends('admin.layout')

@section('content')
    <div class="header">
        <h1>Gestión de Categorías</h1>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3 class="mb-4">Crear Categoría</h3>
            <form action="{{ route('admin.categories.store') }}" method="POST">
                @csrf
                <div class="form-group">
                    <label>Nombre</label>
                    <input type="text" name="name" required placeholder="Ej. Hardware">
                </div>
                <div class="form-group">
                    <label>Descripción</label>
                    <textarea name="description" rows="3" placeholder="Descripción breve..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Guardar Categoría</button>
            </form>
        </div>

        <div class="card table-container" style="margin-top: 0">
            <table>
                <thead>
                    <tr>
                        <th>Categoría</th>
                        <th style="text-align: right;">Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($categories as $category)
                    <tr>
                        <td style="font-weight: 500;">
                            {{ $category->name }}
                            <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: normal;">{{ $category->description }}</div>
                        </td>
                        <td style="text-align: right;">
                            <form action="{{ route('admin.categories.destroy', $category) }}" method="POST" onsubmit="return confirm('¿Eliminar esta categoría?');">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-danger" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Eliminar</button>
                            </form>
                        </td>
                    </tr>
                    @endforeach
                    @if($categories->isEmpty())
                        <tr><td colspan="2" style="text-align: center; color: var(--text-muted);">No hay categorías</td></tr>
                    @endif
                </tbody>
            </table>
        </div>
    </div>
@endsection
