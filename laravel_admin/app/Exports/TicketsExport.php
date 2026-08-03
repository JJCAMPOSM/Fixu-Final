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
            $this->sanitizeCell($ticket->title),
            $this->sanitizeCell($ticket->body),
            ucfirst($ticket->status),
            ucfirst($ticket->priority),
            $ticket->requester ? $this->sanitizeCell($ticket->requester->name) : 'N/A',
            $ticket->category ? $this->sanitizeCell($ticket->category->name) : 'N/A',
            $ticket->team ? $this->sanitizeCell($ticket->team->name) : 'N/A',
            ($ticket->assignee && $ticket->assignee->user) ? $this->sanitizeCell($ticket->assignee->user->name) : 'N/A',
            $ticket->created_at->format('Y-m-d H:i:s'),
        ];
    }

    /**
     * Evita inyección de fórmulas en Excel: título/descripción/nombres son texto
     * libre escrito por solicitantes (rol de bajo privilegio) y se vuelcan tal
     * cual a celdas del .xlsx que luego abre un admin. Si el valor empieza con
     * un carácter que Excel interpreta como inicio de fórmula (=, +, -, @) o
     * un tab/CR, se antepone un apóstrofe para forzar que se trate como texto.
     */
    private function sanitizeCell(?string $value): ?string
    {
        if ($value === null || $value === '') {
            return $value;
        }

        if (preg_match('/^[=+\-@\t\r]/', $value)) {
            return "'" . $value;
        }

        return $value;
    }
}
