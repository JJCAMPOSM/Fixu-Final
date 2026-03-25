<?php

namespace App\Exports;

use App\Models\Ticket;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithMapping;

class TicketsExport implements FromCollection, WithHeadings, WithMapping
{
    /**
    * @return \Illuminate\Support\Collection
    */
    public function collection()
    {
        return Ticket::with(['requester', 'category', 'team', 'assignee.user'])->get();
    }

    public function headings(): array
    {
        return [
            'ID',
            'Título',
            'Descripción',
            'Estado',
            'Prioridad',
            'Solicitante',
            'Categoría',
            'Equipo',
            'Agente Asignado',
            'Fecha de Creación',
        ];
    }

    public function map($ticket): array
    {
        return [
            $ticket->id,
            $ticket->title,
            $ticket->body,
            ucfirst($ticket->status),
            ucfirst($ticket->priority),
            $ticket->requester ? $ticket->requester->name : 'N/A',
            $ticket->category ? $ticket->category->name : 'N/A',
            $ticket->team ? $ticket->team->name : 'N/A',
            ($ticket->assignee && $ticket->assignee->user) ? $ticket->assignee->user->name : 'N/A',
            $ticket->created_at->format('Y-m-d H:i:s'),
        ];
    }
}
