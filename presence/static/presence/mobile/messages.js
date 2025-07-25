// Script pour gérer l'affichage des messages au-dessus de la navbar
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelector('.messages');
    const mainContent = document.querySelector('.main-content');
    
    // Si des messages sont présents, ajouter une classe au contenu principal
    if (messages && messages.children.length > 0) {
        if (mainContent) {
            mainContent.classList.add('has-messages');
        }
        
        // Auto-fermeture des messages après 5 secondes
        setTimeout(function() {
            const alerts = messages.querySelectorAll('.alert');
            alerts.forEach(function(alert) {
                alert.style.animation = 'slideOutToTop 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                setTimeout(function() {
                    alert.remove();
                    // Si plus de messages, retirer la classe
                    if (messages.children.length === 0 && mainContent) {
                        mainContent.classList.remove('has-messages');
                    }
                }, 400);
            });
        }, 5000);
    }
    
    // Gestion des boutons de fermeture des messages
    const closeButtons = document.querySelectorAll('.alert-close');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const alert = this.parentElement;
            alert.style.animation = 'slideOutToTop 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards';
            setTimeout(function() {
                alert.remove();
                // Si plus de messages, retirer la classe
                if (messages && messages.children.length === 0 && mainContent) {
                    mainContent.classList.remove('has-messages');
                }
            }, 400);
        });
    });
});

// Animation de sortie pour les messages
const style = document.createElement('style');
style.textContent = `
@keyframes slideOutToTop {
    from {
        transform: translateY(0);
        opacity: 1;
    }
    to {
        transform: translateY(-100%);
        opacity: 0;
    }
}
`;
document.head.appendChild(style);