document.addEventListener("DOMContentLoaded", function () {
    const burger = document.querySelector(".burger-btn");
    const nav = document.querySelector(".mobile-nav");
    const overlay = document.querySelector(".menu-overlay");
    const closeNav = document.querySelector(".close-nav");
    const body = document.body;

    // Fonction pour ouvrir le menu
    function openMenu() {
        nav.classList.add("active");
        overlay.classList.add("active");
        burger.setAttribute("aria-expanded", "true");
        body.style.overflow = "hidden"; // Empêche le scroll du body
    }

    // Fonction pour fermer le menu
    function closeMenu() {
        nav.classList.remove("active");
        overlay.classList.remove("active");
        burger.setAttribute("aria-expanded", "false");
        body.style.overflow = ""; // Restaure le scroll
    }

    // Événements
    burger.addEventListener("click", openMenu);
    closeNav.addEventListener("click", closeMenu);
    overlay.addEventListener("click", closeMenu);

    // Fermer le menu avec Escape
    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape" && nav.classList.contains("active")) {
            closeMenu();
        }
    });

    // Fermer le menu quand on clique sur un lien (sauf logout)
    const navLinks = nav.querySelectorAll("a:not(.logout-form button)");
    navLinks.forEach(link => {
        link.addEventListener("click", closeMenu);
    });

    // Gestion du swipe pour fermer le menu
    let touchStartX = 0;
    let touchEndX = 0;

    nav.addEventListener("touchstart", function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });

    nav.addEventListener("touchend", function(e) {
        touchEndX = e.changedTouches[0].screenX;
        if (touchStartX - touchEndX > 50) { // Swipe vers la gauche
            closeMenu();
        }
    });
});