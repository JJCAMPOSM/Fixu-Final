document.addEventListener('DOMContentLoaded', function () {
    // Skip character counters on auth pages (login/register) for minimalist design
    const isAuthPage = document.body.classList.contains('auth-bg');
    if (isAuthPage) {
        return; // Exit early, no counters on auth pages
    }

    // 5. VALIDACIÓN DE LÍMITES DE LONGITUD (CRÍTICO DE UX)
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea');

    inputs.forEach(input => {
        // Detect maxlength or assign logical defaults
        let maxLength = input.getAttribute('maxlength');

        if (!maxLength) {
            // Assign logical defaults if not present
            if (input.tagName === 'TEXTAREA') {
                maxLength = 500;
            } else {
                maxLength = 100; // Default for text inputs
            }
            input.setAttribute('maxlength', maxLength);
        }

        // Create counter element
        const counter = document.createElement('small');
        counter.className = 'char-counter';
        counter.textContent = `${input.value.length} / ${maxLength}`;

        // Insert counter after the input (and its error message container if exists)
        // We try to find the parent .mb-3 or similar container to append at the end
        const container = input.closest('div') || input.parentElement;
        container.appendChild(counter);

        // Update function
        const updateCounter = () => {
            const currentLength = input.value.length;
            counter.textContent = `${currentLength} / ${maxLength}`;

            if (currentLength >= maxLength) {
                counter.classList.add('limit-reached');
                input.classList.add('limit-reached');
            } else {
                counter.classList.remove('limit-reached');
                input.classList.remove('limit-reached');
            }
        };

        // Listeners
        input.addEventListener('input', updateCounter);

        // Initial check
        updateCounter();
    });
});
