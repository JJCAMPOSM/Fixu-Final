document.addEventListener('DOMContentLoaded', function() {
    console.log('Script de feedback cargado');
    
    const ratingCircles = document.querySelectorAll('.rating-circle');
    const ratingInput = document.getElementById('rating');
    let selectedRating = 0;

    // Función para actualizar la visualización de los círculos
    function updateCircles(value) {
        console.log('Actualizando círculos a valor:', value);
        ratingCircles.forEach(circle => {
            const circleValue = parseInt(circle.getAttribute('data-value'));
            if (circleValue <= value) {
                circle.classList.add('selected');
                circle.style.backgroundColor = '#0d6efd';
                circle.style.borderColor = '#0d6efd';
                circle.style.color = 'white';
                circle.style.fontWeight = 'bold';
            } else {
                circle.classList.remove('selected');
                circle.style.backgroundColor = '#f8f9fa';
                circle.style.borderColor = '#e4e5e9';
                circle.style.color = '#6c757d';
                circle.style.fontWeight = 'normal';
            }
        });
    }

    // Agregar eventos a los círculos
    ratingCircles.forEach(circle => {
        // Estilo inicial para el hover
        circle.addEventListener('mouseover', function() {
            if (!this.classList.contains('selected')) {
                this.style.backgroundColor = '#e9ecef';
                this.style.borderColor = '#adb5bd';
            }
        });

        // Restaurar al quitar el mouse
        circle.addEventListener('mouseout', function() {
            updateCircles(selectedRating);
        });

        // Seleccionar al hacer clic
        circle.addEventListener('click', function() {
            selectedRating = parseInt(this.getAttribute('data-value'));
            console.log('Círculo seleccionado:', selectedRating);
            if (ratingInput) {
                ratingInput.value = selectedRating;
            }
            updateCircles(selectedRating);
        });
    });

    // Inicializar
    updateCircles(0);
    console.log('Eventos de círculos configurados');

    // Manejar envío del formulario
    const feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (selectedRating === 0) {
                alert('Por favor, selecciona una calificación');
                return;
            }

            const formData = {
                calificacion: selectedRating,
                comentario: document.getElementById('comentario').value
            };

            // Enviar datos al servidor
            const ticketId = document.getElementById('feedbackButton').dataset.ticketId;
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
            fetch(`/api/tickets/${ticketId}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-CSRF-Token': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            })
            .then(async response => {
                const ct = response.headers.get('Content-Type') || '';
                if (!response.ok) {
                    const text = await response.text();
                    throw new Error(text || `Error ${response.status}`);
                }
                if (ct.includes('application/json')) {
                    return response.json();
                }
                const text = await response.text();
                throw new Error(text || 'Respuesta no JSON');
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                alert('¡Gracias por tu feedback!');
                
                // Actualizar interfaz
                const feedbackButton = document.getElementById('feedbackButton');
                if (feedbackButton) {
                    feedbackButton.disabled = true;
                    feedbackButton.textContent = 'Feedback Enviado';
                    feedbackButton.classList.remove('btn-primary');
                    feedbackButton.classList.add('btn-secondary');
                }
                
                // Cerrar el modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('feedbackModal'));
                if (modal) modal.hide();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al enviar el feedback: ' + error.message);
            });
        });
    }
});