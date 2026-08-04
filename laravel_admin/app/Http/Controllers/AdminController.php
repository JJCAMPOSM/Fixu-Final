<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Team;
use App\Models\Category;
use App\Models\Requester;
use App\Models\User;

class AdminController extends Controller
{
    public function dashboard(Request $request)
    {
        $startDate = $request->input('start_date', now()->subDays(30)->format('Y-m-d'));
        $endDate = $request->input('end_date', now()->format('Y-m-d'));

        // Obtener tickets resueltos en el rango de fechas
        $closedTickets = \App\Models\Ticket::with(['category', 'assignee.user', 'team'])
            ->where('status', 'resolved')
            ->whereBetween('updated_at', [$startDate . ' 00:00:00', $endDate . ' 23:59:59'])
            ->get();

        // Agrupaciones analíticas
        $ticketsByAgent = $closedTickets->groupBy(function($ticket) {
            return $ticket->assignee && $ticket->assignee->user ? $ticket->assignee->user->name : 'Sin Asignar';
        })->map->count();

        $ticketsByCategory = $closedTickets->groupBy(function($ticket) {
            return $ticket->category ? $ticket->category->name : 'Sin Categoría';
        })->map->count();

        $ticketsByTeam = $closedTickets->groupBy(function($ticket) {
            return $ticket->team ? $ticket->team->name : 'Sin Equipo';
        })->map->count();

        return view('admin.dashboard', [
            'ticketsByAgent' => $ticketsByAgent,
            'ticketsByCategory' => $ticketsByCategory,
            'ticketsByTeam' => $ticketsByTeam,
            'start_date' => $startDate,
            'end_date' => $endDate,
        ]);
    }

    public function teams()
    {
        return view('admin.teams', ['teams' => Team::latest()->get()]);
    }

    public function storeTeam(Request $request)
    {
        $request->validate(['name' => 'required|string|max:120|unique:teams']);
        Team::create($request->only('name'));
        return redirect()->route('admin.teams.index')->with('success', 'Equipo creado exitosamente.');
    }

    public function destroyTeam(Team $team)
    {
        $team->delete();
        return redirect()->route('admin.teams.index')->with('success', 'Equipo eliminado exitosamente.');
    }

    public function categories()
    {
        return view('admin.categories', ['categories' => Category::latest()->get()]);
    }

    public function storeCategory(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:120|unique:categories',
            'description' => 'nullable|string',
        ]);
        Category::create($request->only(['name', 'description']) + ['color' => '#6366f1']);
        return redirect()->route('admin.categories.index')->with('success', 'Categoría creada exitosamente.');
    }

    public function destroyCategory(Category $category)
    {
        $category->delete();
        return redirect()->route('admin.categories.index')->with('success', 'Categoría eliminada exitosamente.');
    }

    public function requesters()
    {
        return view('admin.requesters', ['requesters' => Requester::latest()->get()]);
    }

    public function storeRequester(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:120',
            'email' => 'required|email|max:255|unique:requesters,email|unique:users,email',
            'phone' => 'required|digits_between:7,20',
            'password' => 'required|string|min:8',
        ]);

        Requester::create($request->only(['name', 'email', 'phone']));

        // Además del perfil, crea la cuenta de acceso (rol solicitante) con la
        // que esta persona podrá loguearse en la web; sin esto, el solicitante
        // quedaba registrado pero no tenía forma de iniciar sesión.
        $user = new User();
        $user->name = $request->name;
        $user->email = $request->email;
        $user->role = 'requester';
        // Compatibility with Flask's bcrypt checking
        $user->password_hash = password_hash($request->password, PASSWORD_BCRYPT);
        $user->save();

        return redirect()->route('admin.requesters.index')->with('success', 'Solicitante creado exitosamente.');
    }

    public function destroyRequester(Requester $requester)
    {
        $requester->delete();
        return redirect()->route('admin.requesters.index')->with('success', 'Solicitante eliminado exitosamente.');
    }

    public function agents()
    {
        return view('admin.agents', ['agents' => User::where('role', 'agent')->latest()->get()]);
    }

    public function storeAgent(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:120',
            'email' => 'required|email|max:255|unique:users',
            'password' => 'required|string|min:8',
        ]);
        
        $user = new User();
        $user->name = $request->name;
        $user->email = $request->email;
        // In this architecture, Flask expects 'agent' role
        $user->role = 'agent';
        // Compatibility with Flask's bcrypt checking
        $user->password_hash = password_hash($request->password, PASSWORD_BCRYPT);
        $user->save();

        return redirect()->route('admin.agents.index')->with('success', 'Agente creado exitosamente.');
    }

    public function destroyAgent(User $user)
    {
        if($user->role !== 'agent') {
            return redirect()->route('admin.agents.index')->with('error', 'Solo se pueden eliminar agentes.');
        }
        $user->delete();
        return redirect()->route('admin.agents.index')->with('success', 'Agente eliminado exitosamente.');
    }

    // --- Team Members ---

    public function teamMembers(Team $team)
    {
        // Obtener los miembros actuales del equipo
        $members = $team->members()->with('user')->get();
        // Obtener agentes que no están en este equipo
        $agentsNotInTeam = User::where('role', 'agent')
            ->whereNotIn('id', $members->pluck('user_id'))
            ->get();
            
        return view('admin.team_members', [
            'team' => $team,
            'members' => $members,
            'available_agents' => $agentsNotInTeam
        ]);
    }

    public function addTeamMember(Request $request, Team $team)
    {
        $request->validate(['user_id' => 'required|exists:users,id']);
        
        $user = User::findOrFail($request->user_id);
        if($user->role !== 'agent') {
            return back()->with('error', 'El usuario seleccionado no es un agente.');
        }

        // Check if already in team
        if($team->members()->where('user_id', $user->id)->exists()) {
            return back()->with('error', 'El agente ya pertenece al equipo.');
        }

        \App\Models\TeamMember::create([
            'team_id' => $team->id,
            'user_id' => $user->id,
            'is_lead' => false
        ]);

        return back()->with('success', 'Agente asignado al equipo exitosamente.');
    }

    public function removeTeamMember(\App\Models\TeamMember $teamMember)
    {
        $teamMember->delete();
        return back()->with('success', 'Agente removido del equipo.');
    }

    // --- Tickets ---

    public function tickets()
    {
        $tickets = \App\Models\Ticket::with(['requester', 'category', 'team', 'assignee.user'])->orderBy('created_at', 'desc')->get();
        return view('admin.tickets', compact('tickets'));
    }

    public function editTicket(\App\Models\Ticket $ticket)
    {
        $categories = Category::orderBy('name')->get();
        $teams = Team::orderBy('name')->get();
        // Todos los miembros de equipo para filtrar con JS
        $allTeamMembers = \App\Models\TeamMember::with(['user', 'team'])->get();

        return view('admin.tickets_edit', compact('ticket', 'categories', 'teams', 'allTeamMembers'));
    }

    public function updateTicket(Request $request, \App\Models\Ticket $ticket)
    {
        // El solicitante no es editable desde aquí: lo define quien crea el
        // ticket, no el admin.
        $request->validate([
            'title' => 'required|string|max:200',
            'body' => 'required|string',
            'category_id' => 'nullable|exists:categories,id',
            'team_id' => 'nullable|exists:teams,id',
            'assignee_team_member_id' => 'nullable|exists:team_members,id',
            'status' => 'required|in:pending,assigned,in_progress,on_hold,cancelled,resolved',
            'priority' => 'required|in:low,medium,high',
            'building' => 'nullable|string|max:80',
            'classroom' => 'nullable|string|max:80',
            'equipment_type' => 'nullable|string|max:80',
        ]);

        $assigneeId = $request->assignee_team_member_id ?: null;
        $status = $request->status;
        // Al asignar un agente a un ticket todavía "pendiente", el estado
        // avanza automáticamente a "asignado" (mismo criterio que la web Flask).
        if ($assigneeId !== null && $status === 'pending') {
            $status = 'assigned';
        }

        $ticket->update([
            'title' => $request->title,
            'body' => $request->body,
            'category_id' => $request->category_id ?: null,
            'team_id' => $request->team_id ?: null,
            'assignee_team_member_id' => $assigneeId,
            'status' => $status,
            'priority' => $request->priority,
            'building' => $request->building ?: null,
            'classroom' => $request->classroom ?: null,
            'equipment_type' => $request->equipment_type ?: null,
        ]);

        return redirect()->route('admin.tickets.index')->with('success', 'Ticket actualizado exitosamente.');
    }

    public function logout(Request $request)
    {
        $request->session()->forget('admin_authenticated');
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect('/auth/logout');
    }
}
