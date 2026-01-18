// Minimal JavaScript for UX enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Enhance location card selection with visual feedback
    const locationCards = document.querySelectorAll('.location-card');
    locationCards.forEach(function(card) {
        card.addEventListener('click', function(e) {
            // If clicking on the card but not the radio button, trigger the radio
            if (e.target !== card.querySelector('input[type="radio"]')) {
                const radio = card.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                    // Remove selected class from siblings
                    const siblings = card.parentElement.querySelectorAll('.location-card');
                    siblings.forEach(function(sibling) {
                        sibling.classList.remove('selected');
                    });
                    card.classList.add('selected');
                }
            }
        });
    });

    // Handle deep link fallback for mobile navigation
    const navigateForm = document.querySelector('form[action*="navigate_action"]');
    if (navigateForm) {
        navigateForm.addEventListener('submit', function(e) {
            // On mobile, try to open deep link before form submission
            const deepLink = document.getElementById('deep-link');
            if (deepLink && /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                // Small delay to let form submit, then try deep link
                setTimeout(function() {
                    window.location.href = deepLink.href;
                }, 100);
            }
        });
    }
});
