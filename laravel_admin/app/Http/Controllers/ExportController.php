<?php

namespace App\Http\Controllers;

use App\Models\Ticket;
use App\Exports\TicketsExport;
use Maatwebsite\Excel\Facades\Excel;
use Barryvdh\DomPDF\Facade\Pdf;
use Illuminate\Http\Request;

class ExportController extends Controller
{
    public function ticketsExcel()
    {
        return Excel::download(new TicketsExport, 'tickets_' . now()->format('Ymd_His') . '.xlsx');
    }

    public function ticketsPdf()
    {
        $tickets = Ticket::with(['requester', 'category', 'team', 'assignee.user'])->get();
        
        $pdf = Pdf::loadView('admin.exports.tickets_pdf', compact('tickets'));
        
        return $pdf->download('tickets_' . now()->format('Ymd_His') . '.pdf');
    }
}
