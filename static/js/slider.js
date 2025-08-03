let currentIndex = 0;

function showSlide(index) {
    const slides = document.querySelector('.slides');
    const totalSlides = document.querySelectorAll('.slide').length;

    if (index >= totalSlides) currentIndex = 0;
    if (index < 0) currentIndex = totalSlides - 1;

    slides.style.transform = `translateX(-${currentIndex * 100}%)`;
}

function nextSlide() {
    currentIndex++;
    showSlide(currentIndex);
}

function prevSlide() {
    currentIndex--;
    showSlide(currentIndex);
}

// Sayfa yüklenirken ilk slide'ı göster
showSlide(currentIndex);

// 🛠 **Otomatik geçiş fonksiyonu** (her 5 saniyede bir geçiş yapar)
setInterval(nextSlide, 5000);