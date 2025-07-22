document.addEventListener('DOMContentLoaded', function() {
    const btnFutures = document.getElementById('btn-sessions-futures');
    const btnPassees = document.getElementById('btn-sessions-passees');
    const sectionFutures = document.getElementById('section-futures');
    const sectionPassees = document.getElementById('section-passees');

    // Fonction pour changer de vue
    function switchView(activeBtn, inactiveBtn, activeSection, inactiveSection) {
        // Mise à jour des boutons
        activeBtn.classList.add('active');
        inactiveBtn.classList.remove('active');
        
        // Mise à jour des sections
        activeSection.style.display = 'block';
        activeSection.classList.add('active');
        inactiveSection.style.display = 'none';
        inactiveSection.classList.remove('active');
    }

    // Gestion du clic sur "Sessions futures"
    btnFutures.addEventListener('click', function() {
        switchView(btnFutures, btnPassees, sectionFutures, sectionPassees);
    });

    // Gestion du clic sur "Sessions passées"
    btnPassees.addEventListener('click', function() {
        switchView(btnPassees, btnFutures, sectionPassees, sectionFutures);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const btnFutures = document.getElementById('btn-sessions-futures');
    const btnPassees = document.getElementById('btn-sessions-passees');
    const sectionFutures = document.getElementById('section-futures');
    const sectionPassees = document.getElementById('section-passees');

    // Vérifier que tous les éléments existent
    if (!btnFutures || !btnPassees || !sectionFutures || !sectionPassees) {
        console.error('Éléments manquants pour le filtrage des sessions');
        return;
    }

    // Fonction pour changer de vue
    function switchView(activeBtn, inactiveBtn, activeSection, inactiveSection) {
        // Mise à jour des boutons
        activeBtn.classList.add('active');
        inactiveBtn.classList.remove('active');
        
        // Mise à jour des sections
        activeSection.style.display = 'block';
        activeSection.classList.add('active');
        inactiveSection.style.display = 'none';
        inactiveSection.classList.remove('active');
    }

    // Gestion du clic sur "Sessions futures"
    btnFutures.addEventListener('click', function(e) {
        e.preventDefault();
        switchView(btnFutures, btnPassees, sectionFutures, sectionPassees);
    });

    // Gestion du clic sur "Sessions passées"
    btnPassees.addEventListener('click', function(e) {
        e.preventDefault();
        switchView(btnPassees, btnFutures, sectionPassees, sectionFutures);
    });
});