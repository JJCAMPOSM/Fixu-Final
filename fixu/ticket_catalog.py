"""Catálogos fijos de ubicación/equipo para la creación de tickets desde el
solicitante (web y App Móvil). Compartido para que la validación del backend
y las opciones mostradas en los formularios sean siempre las mismas."""

BUILDINGS = ['Edificio A', 'Edificio B', 'Edificio C', 'Edificio D', 'Biblioteca']
CLASSROOMS = ['Aula 101', 'Aula 102', 'Aula 203', 'Aula 204', 'Laboratorio 1']
EQUIPMENT_TYPES = ['Proyector', 'Computadora', 'Impresora', 'Aire acondicionado', 'Pizarrón electrónico']

# Flujo de estados de un ticket (ver rúbrica del proyecto):
#   Pendiente -> Asignado (automático al asignar agente) -> En proceso / En espera / Cancelado / Resuelto
# 'Pendiente' y 'Asignado' se fijan por el sistema/admin al crear o asignar;
# el agente solo puede mover el ticket entre los 4 estados de STATUS_AGENT_CHOICES.
STATUS_LABELS = {
    'pending': 'Pendiente',
    'assigned': 'Asignado',
    'in_progress': 'En proceso',
    'on_hold': 'En espera',
    'cancelled': 'Cancelado',
    'resolved': 'Resuelto',
}

STATUS_ADMIN_CHOICES = [(k, v) for k, v in STATUS_LABELS.items()]
STATUS_AGENT_CHOICES = [(k, STATUS_LABELS[k]) for k in ('in_progress', 'on_hold', 'cancelled', 'resolved')]

# Estados en los que el solicitante todavía puede cancelar su propio ticket
# (rúbrica: "puede cancelar un ticket si aún no ha sido atendido").
CANCELABLE_BY_REQUESTER = ('pending', 'assigned')
