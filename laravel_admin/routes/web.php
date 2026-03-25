<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AdminController;

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
});
