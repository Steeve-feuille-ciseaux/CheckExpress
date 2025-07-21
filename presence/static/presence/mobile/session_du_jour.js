/**
 * Gestion des participants - Version mobile optimisée
 * Permet de cliquer n'importe où sur la carte du participant
 */

function toggleParticipant(element) {
    // Vérification que l'élément existe
    if (!element) return;
    
    // Trouve la checkbox associée
    const checkbox = element.querySelector('input[type="checkbox"]');
    if (!checkbox) return;
    
    // Toggle de l'état
    const isCurrentlySelected = element.classList.contains('selected');
    
    if (isCurrentlySelected) {
        // Désélectionner
        element.classList.remove('selected');
        checkbox.checked = false;
    } else {
        // Sélectionner
        element.classList.add('selected');
        checkbox.checked = true;
    }
    
    // Mettre à jour le compteur
    updateCounter();
    
    // Feedback haptique léger sur mobile (si supporté)
    if ('vibrate' in navigator) {
        navigator.vibrate(50);
    }
}

function selectAllParticipants() {
    const items = document.querySelectorAll('.participant-item');
    let changedCount = 0;
    
    items.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox && !checkbox.checked) {
            item.classList.add('selected');
            checkbox.checked = true;
            changedCount++;
        }
    });
    
    updateCounter();
    
    // Feedback visuel pour l'action globale
    if (changedCount > 0) {
        showFeedback(`${changedCount} participant(s) sélectionné(s)`);
    }
}

function clearAllParticipants() {
    const items = document.querySelectorAll('.participant-item');
    let changedCount = 0;
    
    items.forEach(item => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox && checkbox.checked) {
            item.classList.remove('selected');
            checkbox.checked = false;
            changedCount++;
        }
    });
    
    updateCounter();
    
    // Feedback visuel pour l'action globale
    if (changedCount > 0) {
        showFeedback(`${changedCount} participant(s) désélectionné(s)`);
    }
}

function updateCounter() {
    const selectedItems = document.querySelectorAll('.participant-item.selected');
    const counterElement = document.getElementById('selectedCount');
    
    if (counterElement) {
        counterElement.textContent = selectedItems.length;
        
        // Animation du compteur quand il change
        counterElement.parentElement.style.transform = 'scale(1.05)';
        setTimeout(() => {
            counterElement.parentElement.style.transform = 'scale(1)';
        }, 150);
    }
}

function showFeedback(message) {
    // Création d'un toast simple pour le feedback
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Affichage avec animation
    setTimeout(() => toast.style.opacity = '1', 10);
    
    // Suppression après 2 secondes
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 2000);
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation des participants...');
    
    // Marquer les éléments déjà sélectionnés au chargement
    const checkboxes = document.querySelectorAll('.participant-item input[type="checkbox"]');
    let initialSelectedCount = 0;
    
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            const participantItem = checkbox.closest('.participant-item');
            if (participantItem) {
                participantItem.classList.add('selected');
                initialSelectedCount++;
            }
        }
    });
    
    // Mise à jour initiale du compteur
    updateCounter();
    
    // Amélioration de l'accessibilité - support clavier
    const participantItems = document.querySelectorAll('.participant-item');
    participantItems.forEach((item, index) => {
        // Rendre focusable au clavier
        item.setAttribute('tabindex', '0');
        item.setAttribute('role', 'checkbox');
        
        // Support des touches Entrée et Espace
        item.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleParticipant(item);
            }
        });
        
        // Amélioration de l'attribut aria-checked
        const updateAriaChecked = () => {
            const isSelected = item.classList.contains('selected');
            item.setAttribute('aria-checked', isSelected);
        };
        
        // Observer les changements de classe pour mettre à jour aria-checked
        const observer = new MutationObserver(updateAriaChecked);
        observer.observe(item, { 
            attributes: true, 
            attributeFilter: ['class'] 
        });
        
        // État initial
        updateAriaChecked();
    });
    
    // Gestion des boutons rapides avec le clavier
    const quickButtons = document.querySelectorAll('.quick-btn');
    quickButtons.forEach(button => {
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                button.click();
            }
        });
    });
    
    console.log(`✅ ${participantItems.length} participants initialisés (${initialSelectedCount} présélectionnés)`);
});

// Fonction utilitaire pour déboguer (à supprimer en production)
function debugParticipants() {
    const selected = document.querySelectorAll('.participant-item.selected');
    const checked = document.querySelectorAll('.participant-item input[type="checkbox"]:checked');
    
    console.log('🔍 État des participants :');
    console.log(`- Cartes sélectionnées: ${selected.length}`);
    console.log(`- Checkboxes cochées: ${checked.length}`);
    
    return {
        selectedCards: selected.length,
        checkedBoxes: checked.length,
        synchronized: selected.length === checked.length
    };
}