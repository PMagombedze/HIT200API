// Store location (hardcoded for now - should be configured in backend)
const STORE_LOCATION = { lat: -17.8630, lng: 31.0571 }; // Harare Institute of Technology coordinates
const GEOAPIFY_KEY = 'e5e02bad78084e5eb85e8263f7d05800'; // Replace with actual key
let map;
let marker;
let deliveryAddress = '';
let deliveryDistance = 0;
let deliveryFee = 0;

function initMap() {
    // Create map with Geoapify tiles
    map = L.map('delivery-map').setView([STORE_LOCATION.lat, STORE_LOCATION.lng], 12);
    
    // Add Geoapify tile layer
    L.tileLayer('https://maps.geoapify.com/v1/tile/{style}/{z}/{x}/{y}.png?apiKey={apiKey}', {
        attribution: 'Powered by <a href="https://www.geoapify.com/" target="_blank">Geoapify</a>',
        maxZoom: 20,
        apiKey: GEOAPIFY_KEY,
        style: 'osm-bright' // Try also: 'dark', 'osm-bright', 'osm-bright-grey'
    }).addTo(map);

    // Add store location marker
    L.marker([STORE_LOCATION.lat, STORE_LOCATION.lng])
        .addTo(map)
        .bindPopup("Our Store")
        .openPopup();

    // Initialize address search with autocomplete
    const addressInput = document.getElementById('delivery-address');
    const suggestionsList = document.createElement('ul');
    suggestionsList.setAttribute('class', 'address-suggestions');
    addressInput.parentNode.insertBefore(suggestionsList, addressInput.nextSibling);

    // Add click event listeners to map
    map.on('click', function(e) {
        const clickedLat = e.latlng.lat;
        const clickedLng = e.latlng.lng;
        reverseGeocode(clickedLat, clickedLng, addressInput);
    });

    addressInput.addEventListener('input', debounce(async () => {
        if (addressInput.value.length > 3) {
            try {
                const response = await fetch(`https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(addressInput.value)}&filter=countrycode:zw&apiKey=${GEOAPIFY_KEY}`);
                const data = await response.json();
                
                suggestionsList.innerHTML = '';
                if (data.features && data.features.length > 0) {
                    data.features.forEach(feature => {
                        const li = document.createElement('li');
                        li.textContent = feature.properties.formatted;
                        li.style.cursor = 'pointer';
                        li.addEventListener('click', () => {
                            addressInput.value = feature.properties.formatted;
                            deliveryAddress = feature.properties.formatted;
                            calculateDeliveryFee([feature.properties.lat, feature.properties.lon]);
                            suggestionsList.innerHTML = '';
                        });
                        suggestionsList.appendChild(li);
                    });
                }
            } catch (error) {
                console.error('Autocomplete error:', error);
            }
        } else {
            suggestionsList.innerHTML = '';
        }
    }, 500));
}

async function reverseGeocode(lat, lng, addressInput) {
    try {
        const response = await fetch(`https://api.geoapify.com/v1/geocode/reverse?lat=${lat}&lon=${lng}&apiKey=${GEOAPIFY_KEY}`);
        const data = await response.json();
        
        if (data.features && data.features.length > 0) {
            const address = data.features[0].properties.formatted;
            addressInput.value = address;
            deliveryAddress = address;
            calculateDeliveryFee([lat, lng]);
        }
    } catch (error) {
        console.error('Reverse geocoding error:', error);
    }
}

async function geocodeAddress(address) {
    try {
        const response = await fetch(`https://api.geoapify.com/v1/geocode/search?text=${encodeURIComponent(address)}&filter=countrycode:zw&apiKey=${GEOAPIFY_KEY}`);
        const data = await response.json();
        
        if (data.features && data.features.length > 0) {
            const feature = data.features[0];
            deliveryAddress = feature.properties.formatted;
            calculateDeliveryFee([feature.properties.lat, feature.properties.lon]);
        }
    } catch (error) {
        console.error('Geocoding error:', error);
    }
}

function calculateDeliveryFee(destination) {
    // Use Leaflet's built-in distance calculation
    const from = L.latLng(STORE_LOCATION.lat, STORE_LOCATION.lng);
    const to = L.latLng(destination[0], destination[1]);
    const distanceMeters = from.distanceTo(to);
    
    // Convert to kilometers with 1 decimal place
    const distanceKm = distanceMeters / 1000;
    deliveryDistance = (Math.round(distanceKm * 10) / 10);
    
    // Calculate fee: $3 per 10km, minimum $2
    deliveryFee = Math.max(2, Math.ceil(distanceKm / 10) * 3);
    
    updateDeliveryInfo();
    updateMapMarker(destination);
}

function updateMapMarker(position) {
    if (marker) {
        map.removeLayer(marker);
    }
    
    marker = L.marker(position).addTo(map)
        .bindPopup("Delivery Location")
        .openPopup();
    
    // Create a line between store and delivery location
    if (window.deliveryLine) {
        map.removeLayer(window.deliveryLine);
    }
    window.deliveryLine = L.polyline([
        [STORE_LOCATION.lat, STORE_LOCATION.lng],
        position
    ], {color: 'blue'}).addTo(map);
    
    // Fit bounds to show both markers
    const bounds = L.latLngBounds([
        [STORE_LOCATION.lat, STORE_LOCATION.lng],
        position
    ]);
    map.fitBounds(bounds, {padding: [50, 50]});
}

function updateDeliveryInfo() {
    document.getElementById('delivery-distance').textContent = `${deliveryDistance} km`;
    document.getElementById('delivery-fee').textContent = `$${deliveryFee.toFixed(2)}`;
    updateCartTotal();
}

function updateCartTotal() {
    const cartTotal = parseFloat(document.getElementById('cart-total').textContent);
    const grandTotal = cartTotal + deliveryFee;
    document.getElementById('grand-total').textContent = `${grandTotal.toFixed(2)}`;
}

function debounce(func, timeout = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('delivery-map')) {
        initMap();
    }
});