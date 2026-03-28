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

    public function closedTicketsPdf(Request $request)
    {
        $startDate = $request->input('start_date', now()->subDays(30)->format('Y-m-d'));
        $endDate = $request->input('end_date', now()->format('Y-m-d'));

        $tickets = Ticket::with(['requester', 'category', 'team', 'assignee.user'])
            ->whereIn('status', ['closed', 'solved'])
            ->whereBetween('updated_at', [$startDate . ' 00:00:00', $endDate . ' 23:59:59'])
            ->orderBy('updated_at', 'desc')
            ->get();
        
        $pdf = Pdf::loadView('admin.exports.closed_tickets_pdf', compact('tickets', 'startDate', 'endDate'));
        $pdf->setPaper('a4', 'landscape'); // Mejor visualización para reportes con columnas

        return $pdf->download('Reporte_KPI_Tickets_Resueltos_' . now()->format('Ymd') . '.pdf');
    }
}
