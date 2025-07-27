document.addEventListener('DOMContentLoaded', function() {
    const exportLinks = document.querySelectorAll('.export-link');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    exportLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Afficher l'overlay de chargement
            loadingOverlay.style.display = 'flex';
            
            // Masquer l'overlay après 3 secondes (temps estimé de génération)
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 3000);
        });
    });

    // Animation des cartes au scroll (optimisée pour mobile)
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -30px 0px'  // Réduit pour mobile
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observer toutes les cartes avec animation mobile-friendly
    document.querySelectorAll('.fade-in-mobile').forEach(card => {
        observer.observe(card);
    });

    // Animation des statistiques (réduite sur mobile)
    function animateNumbers() {
        const isMobile = window.innerWidth <= 768;
        const frames = isMobile ? 20 : 30; // Moins de frames sur mobile
        
        document.querySelectorAll('.stat-number').forEach(stat => {
            const target = parseInt(stat.textContent);
            const increment = target / frames;
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    stat.textContent = target;
                    clearInterval(timer);
                } else {
                    stat.textContent = Math.floor(current);
                }
            }, isMobile ? 40 : 50); // Plus rapide sur mobile
        });
    }

    // Démarrer l'animation des chiffres
    setTimeout(animateNumbers, 300);

    // Gestion du swipe sur mobile pour les cartes
    if ('ontouchstart' in window) {
        let startX, startY, distX, distY;
        const threshold = 100; // Distance minimum pour un swipe
        
        document.addEventListener('touchstart', function(e) {
            const touch = e.touches[0];
            startX = touch.pageX;
            startY = touch.pageY;
        });
        
        document.addEventListener('touchmove', function(e) {
            e.preventDefault(); // Empêche le scroll pendant le swipe
        }, { passive: false });
        
        document.addEventListener('touchend', function(e) {
            const touch = e.changedTouches[0];
            distX = touch.pageX - startX;
            distY = touch.pageY - startY;
            
            // Détection du swipe horizontal
            if (Math.abs(distX) > Math.abs(distY) && Math.abs(distX) > threshold) {
                // Feedback visuel léger sur swipe
                const card = e.target.closest('.export-card');
                if (card) {
                    card.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        card.style.transform = '';
                    }, 150);
                }
            }
        });
    }

    // Optimisation des performances sur mobile
    let ticking = false;
    
    function updateOnScroll() {
        // Réduire les calculs pendant le scroll sur mobile
        if (!ticking) {
            requestAnimationFrame(() => {
                // Actions pendant le scroll si nécessaire
                ticking = false;
            });
            ticking = true;
        }
    }
    
    if (window.innerWidth <= 768) {
        window.addEventListener('scroll', updateOnScroll, { passive: true });
    }
});