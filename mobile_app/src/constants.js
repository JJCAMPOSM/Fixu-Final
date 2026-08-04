// Catálogos fijos de ubicación/equipo al reportar una falla. BUILDINGS y
// CLASSROOMS deben coincidir exactamente con fixu/ticket_catalog.py (el
// backend valida contra esas mismas listas). EQUIPMENT_TYPES aquí es
// intencionalmente un subconjunto (solo Proyector/Computadora, los tipos que
// se reportan desde la App Móvil); el backend sigue aceptando la lista
// completa, así que esto no rompe nada, solo restringe las opciones que ve
// el solicitante en el formulario.
export const BUILDINGS = ['Edificio A', 'Edificio B', 'Edificio C', 'Edificio D', 'Biblioteca'];
export const CLASSROOMS = ['Aula 101', 'Aula 102', 'Aula 203', 'Aula 204', 'Laboratorio 1'];
export const EQUIPMENT_TYPES = ['Proyector', 'Computadora'];
