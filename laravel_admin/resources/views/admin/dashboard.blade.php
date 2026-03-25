@extends('admin.layout')

@section('content')
    <div class="header">
        <h1>Dashboard</h1>
    </div>

    <div class="grid-2" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">{{ $teams_count }}</div>
            <div style="color: var(--text-muted); text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;">Equipos</div>
        </div>
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">{{ $categories_count }}</div>
            <div style="color: var(--text-muted); text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;">Categorías</div>
        </div>
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">{{ $requesters_count }}</div>
            <div style="color: var(--text-muted); text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;">Solicitantes</div>
        </div>
        <div class="card" style="text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">{{ $agents_count }}</div>
            <div style="color: var(--text-muted); text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;">Agentes</div>
        </div>
    </div>
@endsection
