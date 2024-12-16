let slideIndex = 0;
const sections = ['section1', 'section2', 'section3', 'section4', 'section5', 'section6', 'section7'];
const maxItems = 6;

function showSlides() {
    fetchImages().then(images => {
        sections.forEach((section, index) => {
            document.getElementById(section).style.backgroundImage = `url(${images[(slideIndex + index) % maxItems]})`;
        });
        updateDots();
        slideIndex = (slideIndex + 1) % maxItems;
        setTimeout(showSlides, 4000);
    });
}

function fetchImages() {
    return Promise.resolve([
        '/static/images/image1.jpg',
        '/static/images/image2.jpg',
        '/static/images/image3.jpg',
        '/static/images/image4.jpg',
        '/static/images/image5.jpg',
        '/static/images/image6.jpg'
    ]);
}

function updateDots() {
    const dots = document.getElementsByClassName('dot');
    for (let i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(' active', '');
    }
    dots[slideIndex].className += ' active';
}

function currentSlide(n) {
    slideIndex = n - 1;
    showSlides();
}

document.addEventListener('DOMContentLoaded', showSlides);