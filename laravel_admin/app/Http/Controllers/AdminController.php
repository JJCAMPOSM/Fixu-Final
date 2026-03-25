<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Team;
use App\Models\Category;
use App\Models\Requester;
use App\Models\User;

class AdminController extends Controller
{
    public function dashboard()
    {
        return view('admin.dashboard', [
            'teams_count' => Team::count(),
            'categories_count' => Category::count(),
            'requesters_count' => Requester::count(),
            'agents_count' => User::where('role', 'agent')->count(),
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
            'color' => 'nullable|string|max:7',
        ]);
        Category::create($request->all());
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
            'email' => 'required|email|max:255|unique:requesters',
            'phone' => 'nullable|string|max:20',
        ]);
        Requester::create($request->all());
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
            'password' => 'required|string|min:6',
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
}
