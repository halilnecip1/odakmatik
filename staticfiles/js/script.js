document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        // Anasayfa linki için özel kontrol (path sadece '/' ise)
        if (link.getAttribute('href') === '/') {
            if (currentPath === '/') {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        }
        // Diğer linkler için
        else if (currentPath.startsWith(link.getAttribute('href')) && link.getAttribute('href') !== '#') {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Swiper Slider başlatma kodu şimdilik kaldırıldı.
    // if (document.querySelector('.swiper-container')) {
    //     const swiper = new Swiper('.swiper-container', {
    //         loop: true,
    //         autoplay: {
    //             delay: 5000,
    //             disableOnInteraction: false,
    //         },
    //         pagination: {
    //             el: '.swiper-pagination',
    //             clickable: true,
    //         },
    //         navigation: {
    //             nextEl: '.swiper-button-next',
    //             prevEl: '.swiper-button-prev',
    //         },
    //     });
    // }
});