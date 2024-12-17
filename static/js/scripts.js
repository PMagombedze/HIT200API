// Global variables
let slideIndex = 0;
const sections = ['section1', 'section2', 'section3', 'section4', 'section5', 'section6', 'section7'];
const maxItems = 6;

// Function to show the slides
function showSlides() {
    fetchImages().then(images => {
        sections.forEach((section, index) => {
            // Assign the background image to the section
            document.getElementById(section).style.backgroundImage = `url(${images[(slideIndex + index) % maxItems]})`;
        });
        // Update the dots
        updateDots();
        // Increment the slideIndex
        slideIndex = (slideIndex + 1) % maxItems;
        // Run the showSlides function every 4 seconds
        setTimeout(showSlides, 4000);
    });
}

// Function to fetch the images
function fetchImages() {
    return Promise.resolve([
        // List of images
        '/static/images/image1.jpg',
        '/static/images/image2.jpg',
        '/static/images/image3.jpg',
        '/static/images/image4.jpg',
        '/static/images/image5.jpg',
        '/static/images/image6.jpg'
    ]);
}

// Function to update the dots
function updateDots() {
    const dots = document.getElementsByClassName('dot');
    // Loop over the dots and remove the active class
    for (let i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(' active', '');
    }
    // Add the active class to the current dot
    dots[slideIndex].className += ' active';
}

// Function to change the current slide
function currentSlide(n) {
    slideIndex = n - 1;
    // Run the showSlides function
    showSlides();
}

// Run the showSlides function after the content has loaded
document.addEventListener('DOMContentLoaded', showSlides);

// This script creates a grid of cards containing product information and a wishlist icon.
// Each card is created dynamically using JavaScript and the data is stored in the 'products' constant.
// When the user clicks on the wishlist icon, the icon is toggled and the 'inWishlist' property of the product is updated.
document.addEventListener('DOMContentLoaded', () => {
    // List of products
    const products = [
      { id: 1, name: 'Product 1', price: '$10.00', image: 'path/to/image1.jpg', inWishlist: false },
      { id: 2, name: 'Product 2', price: '$20.00', image: 'path/to/image2.jpg', inWishlist: false },
      { id: 3, name: 'Product 3', price: '$30.00', image: 'path/to/image3.jpg', inWishlist: false },
      { id: 4, name: 'Product 4', price: '$40.00', image: 'path/to/image4.jpg', inWishlist: false },
      { id: 5, name: 'Product 5', price: '$50.00', image: 'path/to/image5.jpg', inWishlist: false },
      { id: 6, name: 'Product 6', price: '$60.00', image: 'path/to/image6.jpg', inWishlist: false },
    ];
  
    // Get the products grid element
    const productsGrid = document.getElementById('products-grid');
    const wishlistCountElement = document.getElementById('wishlist-count');
    let wishlistCount = 0;

    const updateWishlistCount = () => {
      wishlistCountElement.textContent = wishlistCount;
    };
  
    // Loop over the products and create a card for each one
    products.forEach(product => {
      // Create a column for the card
      const column = document.createElement('div');
      column.className = 'column is-one-fifth';
  
      // Create the card
      const card = document.createElement('div');
      card.className = 'card';
  
      // Create the card image
      const cardImage = document.createElement('div');
      cardImage.className = 'card-image';
  
      // Create the figure element
      const figure = document.createElement('figure');
      figure.className = 'image is-4by3';
  
      // Create the image element
      const img = document.createElement('img');
      img.src = product.image;
      img.alt = product.name;
  
      // Create the wishlist icon
      const wishlistIcon = document.createElement('div');
      wishlistIcon.className = 'wishlist-icon';
      // SVG used for the wishlist icon
      wishlistIcon.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="${product.inWishlist ? 'filled' : ''}">
          <circle cx="12" cy="12" r="12" fill="white"/>
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41 0.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
      `;
      // Add an event listener to the wishlist icon
      wishlistIcon.addEventListener('click', () => {
        product.inWishlist = !product.inWishlist;
        wishlistIcon.querySelector('svg').classList.toggle('filled');
        wishlistCount += product.inWishlist ? 1 : -1;
        updateWishlistCount();
      });
  
      // Append the image and the wishlist icon to the figure element
      figure.appendChild(img);
      figure.appendChild(wishlistIcon);
      cardImage.appendChild(figure);
  
      // Create the card content
      const cardContent = document.createElement('div');
      cardContent.className = 'card-content';
  
      // Create the media element
      const media = document.createElement('div');
      media.className = 'media';
  
      // Create the media content element
      const mediaContent = document.createElement('div');
      mediaContent.className = 'media-content';
  
      // Create the title element
      const title = document.createElement('p');
      title.className = 'title is-5';
      title.textContent = product.name;
  
      // Create the subtitle element
      const subtitle = document.createElement('p');
      subtitle.className = 'subtitle is-6';
      subtitle.textContent = product.price;
  
      // Append the title and the subtitle to the media content element
      mediaContent.appendChild(title);
      mediaContent.appendChild(subtitle);
      media.appendChild(mediaContent);
      cardContent.appendChild(media);
  
      // Append the card image and the card content to the card
      card.appendChild(cardImage);
      card.appendChild(cardContent);
      column.appendChild(card);
      productsGrid.appendChild(column);
    });

    updateWishlistCount();
  });
