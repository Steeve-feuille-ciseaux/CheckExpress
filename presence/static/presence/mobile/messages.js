// Script amélioré pour gérer l'affichage des messages au-dessus de la navbar
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelector('.messages');
    const mainContent = document.querySelector('.main-content');
    
    // Fonction pour calculer la hauteur des messages
    function calculateMessagesHeight() {
        if (!messages || messages.children.length === 0) {
            return 0;
        }
        return messages.offsetHeight;
    }
    
    // Fonction pour ajuster le padding du contenu principal
    function adjustMainContentPadding() {
        if (!mainContent) return;
        
        const messagesHeight = calculateMessagesHeight();
        const navbarHeight = 70; // Hauteur de votre navbar
        
        if (messagesHeight > 0) {
            mainContent.classList.add('has-messages');
            mainContent.style.paddingTop = (navbarHeight + messagesHeight + 20) + 'px';
        } else {
            mainContent.classList.remove('has-messages');
            mainContent.style.paddingTop = '';
        }
    }
    
    // Si des messages sont présents, ajuster le layout
    if (messages && messages.children.length > 0) {
        adjustMainContentPadding();
        
        // Auto-fermeture des messages après 5 secondes
        setTimeout(function() {
            hideAllMessages();
        }, 5000);
    }
    
    // Fonction pour masquer tous les messages
    function hideAllMessages() {
        const alerts = messages ? messages.querySelectorAll('.alert') : [];
        alerts.forEach(function(alert, index) {
            setTimeout(function() {
                hideMessage(alert);
            }, index * 100); // Délai progressif pour un effet plus fluide
        });
    }
    
    // Fonction pour masquer un message spécifique
    function hideMessage(alert) {
        alert.style.animation = 'slideOutToTop 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards';
        setTimeout(function() {
            alert.remove();
            // Réajuster le padding après suppression
            adjustMainContentPadding();
        }, 400);
    }
    
    // Gestion des boutons de fermeture des messages
    const closeButtons = document.querySelectorAll('.alert-close');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const alert = this.closest('.alert');
            hideMessage(alert);
        });
    });
    
    // Réajuster le layout lors du redimensionnement de la fenêtre
    window.addEventListener('resize', function() {
        adjustMainContentPadding();
    });
});

// Animations CSS pour les messages
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

@keyframes slideInFromTop {
    from {
        transform: translateY(-100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.messages .alert {
    animation: slideInFromTop 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
`;
document.head.appendChild(style);