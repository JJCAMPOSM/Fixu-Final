<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AdminController;
use App\Http\Controllers\ExportController;

Route::get('/', function () {
    return redirect()->route('admin.dashboard');
});

Route::prefix('admin')->name('admin.')->group(function () {
    Route::get('/', [AdminController::class, 'dashboard'])->name('dashboard');
    
    // Teams
    Route::get('/teams', [AdminController::class, 'teams'])->name('teams.index');
    Route::post('/teams', [AdminController::class, 'storeTeam'])->name('teams.store');
    Route::delete('/teams/{team}', [AdminController::class, 'destroyTeam'])->name('teams.destroy');
    
    // Categories
    Route::get('/categories', [AdminController::class, 'categories'])->name('categories.index');
    Route::post('/categories', [AdminController::class, 'storeCategory'])->name('categories.store');
    Route::delete('/categories/{category}', [AdminController::class, 'destroyCategory'])->name('categories.destroy');
    
    // Requesters
    Route::get('/requesters', [AdminController::class, 'requesters'])->name('requesters.index');
    Route::post('/requesters', [AdminController::class, 'storeRequester'])->name('requesters.store');
    Route::delete('/requesters/{requester}', [AdminController::class, 'destroyRequester'])->name('requesters.destroy');
    
    // Agents (Users)
    Route::get('/agents', [AdminController::class, 'agents'])->name('agents.index');
    Route::post('/agents', [AdminController::class, 'storeAgent'])->name('agents.store');
    Route::delete('/agents/{user}', [AdminController::class, 'destroyAgent'])->name('agents.destroy');

    // Team Members
    Route::get('/teams/{team}/members', [AdminController::class, 'teamMembers'])->name('teams.members');
    Route::post('/teams/{team}/members', [AdminController::class, 'addTeamMember'])->name('teams.members.add');
    Route::delete('/team-members/{teamMember}', [AdminController::class, 'removeTeamMember'])->name('team-members.remove');

    // Tickets
    Route::get('/tickets', [AdminController::class, 'tickets'])->name('tickets.index');
    Route::get('/tickets/{ticket}/edit', [AdminController::class, 'editTicket'])->name('tickets.edit');
    Route::put('/tickets/{ticket}', [AdminController::class, 'updateTicket'])->name('tickets.update');

    // Exports
    Route::get('/export/tickets/excel', [ExportController::class, 'ticketsExcel'])->name('tickets.export.excel');
    Route::get('/export/tickets/pdf', [ExportController::class, 'ticketsPdf'])->name('tickets.export.pdf');
});
