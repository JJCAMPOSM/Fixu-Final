@extends('admin.layout')

@section('content')
    <div class="header">
        <h1>Editar Ticket #{{ $ticket->id }}</h1>
        <a href="{{ route('admin.tickets.index') }}" class="btn" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white;">&larr; Volver a Tickets</a>
    </div>

    <div class="card" style="max-width: 800px; margin: 0 auto;">
        <form action="{{ route('admin.tickets.update', $ticket) }}" method="POST">
            @csrf
            @method('PUT')
            
            <div class="form-group">
                <label>Título del Ticket</label>
                <input type="text" name="title" value="{{ old('title', $ticket->title) }}" required>
            </div>

            <div class="form-group">
                <label>Descripción</label>
                <textarea name="body" rows="5" required>{{ old('body', $ticket->body) }}</textarea>
            </div>

            @php
                $buildings = ['Edificio A', 'Edificio B', 'Edificio C', 'Edificio D', 'Biblioteca'];
                $classrooms = ['Aula 101', 'Aula 102', 'Aula 203', 'Aula 204', 'Laboratorio 1'];
                $equipmentTypes = ['Proyector', 'Computadora', 'Impresora', 'Aire acondicionado', 'Pizarrón electrónico'];
            @endphp
            <div class="grid-2 mt-4" style="gap: 1.5rem;">
                <!-- Edificio -->
                <div class="form-group">
                    <label>Edificio</label>
                    <select name="building">
                        <option value="">-- Ninguno --</option>
                        @foreach($buildings as $b)
                            <option value="{{ $b }}" {{ (old('building', $ticket->building) == $b) ? 'selected' : '' }}>{{ $b }}</option>
                        @endforeach
                    </select>
                </div>

                <!-- Aula -->
                <div class="form-group">
                    <label>Aula</label>
                    <select name="classroom">
                        <option value="">-- Ninguna --</option>
                        @foreach($classrooms as $c)
                            <option value="{{ $c }}" {{ (old('classroom', $ticket->classroom) == $c) ? 'selected' : '' }}>{{ $c }}</option>
                        @endforeach
                    </select>
                </div>

                <!-- Tipo de equipo -->
                <div class="form-group">
                    <label>Tipo de equipo</label>
                    <select name="equipment_type">
                        <option value="">-- Ninguno --</option>
                        @foreach($equipmentTypes as $e)
                            <option value="{{ $e }}" {{ (old('equipment_type', $ticket->equipment_type) == $e) ? 'selected' : '' }}>{{ $e }}</option>
                        @endforeach
                    </select>
                </div>
            </div>

            <div class="grid-2 mt-4" style="gap: 1.5rem;">
                <!-- Solicitante -->
                <div class="form-group">
                    <label>Solicitante</label>
                    <select name="requester_id" required>
                        @foreach($requesters as $req)
                            <option value="{{ $req->id }}" {{ (old('requester_id', $ticket->requester_id) == $req->id) ? 'selected' : '' }}>
                                {{ $req->name }} ({{ $req->email }})
                            </option>
                        @endforeach
                    </select>
                </div>

                <!-- Categoría -->
                <div class="form-group">
                    <label>Categoría</label>
                    <select name="category_id">
                        <option value="">-- Ninguna --</option>
                        @foreach($categories as $cat)
                            <option value="{{ $cat->id }}" {{ (old('category_id', $ticket->category_id) == $cat->id) ? 'selected' : '' }}>
                                {{ $cat->name }}
                            </option>
                        @endforeach
                    </select>
                </div>

                <!-- Equipo -->
                <div class="form-group">
                    <label>Equipo Encargado</label>
                    <select name="team_id" id="team_select">
                        <option value="">-- Ninguno --</option>
                        @foreach($teams as $team)
                            <option value="{{ $team->id }}" {{ (old('team_id', $ticket->team_id) == $team->id) ? 'selected' : '' }}>
                                {{ $team->name }}
                            </option>
                        @endforeach
                    </select>
                </div>

                <!-- Agente -->
                <div class="form-group">
                    <label>Agente Asignado</label>
                    <select name="assignee_team_member_id" id="agent_select">
                        <option value="">-- Ninguno --</option>
                        <!-- Loaded via JS -->
                    </select>
                </div>

                <!-- Estado -->
                <div class="form-group">
                    <label>Estado</label>
                    <select name="status" required>
                        <option value="pending" {{ (old('status', $ticket->status) == 'pending') ? 'selected' : '' }}>Pendiente</option>
                        <option value="assigned" {{ (old('status', $ticket->status) == 'assigned') ? 'selected' : '' }}>Asignado</option>
                        <option value="in_progress" {{ (old('status', $ticket->status) == 'in_progress') ? 'selected' : '' }}>En proceso</option>
                        <option value="on_hold" {{ (old('status', $ticket->status) == 'on_hold') ? 'selected' : '' }}>En espera</option>
                        <option value="cancelled" {{ (old('status', $ticket->status) == 'cancelled') ? 'selected' : '' }}>Cancelado</option>
                        <option value="resolved" {{ (old('status', $ticket->status) == 'resolved') ? 'selected' : '' }}>Resuelto</option>
                    </select>
                </div>

                <!-- Prioridad -->
                <div class="form-group">
                    <label>Prioridad</label>
                    <select name="priority" required>
                        <option value="low" {{ (old('priority', $ticket->priority) == 'low') ? 'selected' : '' }}>Baja</option>
                        <option value="medium" {{ (old('priority', $ticket->priority) == 'medium') ? 'selected' : '' }}>Media</option>
                        <option value="high" {{ (old('priority', $ticket->priority) == 'high') ? 'selected' : '' }}>Alta</option>
                    </select>
                </div>
            </div>

            <div style="margin-top: 2rem; border-top: 1px solid var(--border); padding-top: 1.5rem; text-align: right;">
                <button type="submit" class="btn btn-primary">Guardar Cambios</button>
            </div>
        </form>
    </div>

    <!-- Data for JS Filtering -->
    <script>
        const allTeamMembers = @json($allTeamMembers);
        const currentAssigneeId = {{ old('assignee_team_member_id', $ticket->assignee_team_member_id ?? 'null') }};
        
        const teamSelect = document.getElementById('team_select');
        const agentSelect = document.getElementById('agent_select');

        function updateAgents() {
            const teamId = parseInt(teamSelect.value);
            agentSelect.innerHTML = '<option value="">-- Ninguno --</option>';
            
            if (!teamId) return;

            const filteredMembers = allTeamMembers.filter(m => m.team_id === teamId);
            
            filteredMembers.forEach(member => {
                const opt = document.createElement('option');
                opt.value = member.id;
                opt.textContent = `${member.user.name} (${member.user.email})`;
                if (member.id === currentAssigneeId) {
                    opt.selected = true;
                }
                agentSelect.appendChild(opt);
            });
        }

        teamSelect.addEventListener('change', updateAgents);
        
        // Initial load
        updateAgents();
    </script>
@endsection
