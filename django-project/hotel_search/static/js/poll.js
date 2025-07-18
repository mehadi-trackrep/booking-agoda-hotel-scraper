// hotel_search/static/js/poll.js

// Get CSRF token from Django's cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrfToken = getCookie('csrftoken');

// Get elements from the HTML
const taskId = document.currentScript.dataset.taskId || "{{ task_id }}"; // Get task_id from data-attribute or Django context
const loadingIndicator = document.getElementById('loading-indicator');
const resultsContainer = document.getElementById('results-container');
const noResultsMessage = document.getElementById('no-results-message');
const errorMessage = document.getElementById('error-message');
const errorDetails = document.getElementById('error-details');
const hotelCardTemplate = document.getElementById('hotel-card-template');

function startPolling(pollUrl, hotelsGrid, loadingSpinner, noResultsMessage, cardTemplate, csrfToken) {
    const interval = setInterval(() => {
        fetch(pollUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Always update the UI with the latest data on each poll.
                if (data.hotels && data.hotels.length > 0) {
                    loadingIndicator.classList.add('hidden');
                    noResultsMessage.classList.add('hidden');
                    updateHotelsGrid(data.hotels, hotelsGrid, cardTemplate, csrfToken);
                    hotelsGrid.classList.remove('hidden');
                }

                // Stop polling only when the task is fully complete (SUCCESS or FAILURE).
                if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
                    clearInterval(interval);
                    loadingIndicator.classList.add('hidden'); // Ensure it's hidden at the end.

                    // If the task finished but we have no hotels, show the "no results" message.
                    if (data.hotels.length === 0) {
                        noResultsMessage.classList.remove('hidden');
                    }

                    // If there was an error (either from a FAILED task or a partial error on SUCCESS)
                    if (data.error) {
                        errorMessage.classList.remove('hidden');
                        errorDetails.textContent = data.error;
                    }
                }
            })
            .catch(error => {
                clearInterval(interval);
                console.error('Error polling for results:', error);
                loadingIndicator.classList.add('hidden');
                errorMessage.classList.remove('hidden');
                errorDetails.textContent = `Could not fetch results: ${error.message}. Please try again later.`;
            });
    }, 5000); // Poll every 5 seconds
}

function updateHotelsGrid(hotels, hotelsGrid, cardTemplate, csrfToken) {
    hotelsGrid.innerHTML = ''; // Clear previous results
    hotels.forEach(hotel => {
        const card = cardTemplate.content.cloneNode(true);
        
        card.querySelector('.hotel-image').src = hotel.image_url || 'https://placehold.co/600x400/E0F2F7/000000?text=No+Image';
        card.querySelector('.hotel-name').textContent = hotel.name || 'N/A';
        card.querySelector('.hotel-source').textContent = `Source: ${hotel.source || 'N/A'}`;
        card.querySelector('.hotel-location').textContent = hotel.location || 'N/A';
        card.querySelector('.hotel-price').textContent = hotel.price || 'N/A';
        card.querySelector('.hotel-rating').textContent = hotel.rating || 'N/A';
        card.querySelector('.hotel-url').href = hotel.hotel_url || '#';

        const bookmarkBtn = card.querySelector('.bookmark-btn');
        const bookmarkIcon = bookmarkBtn.querySelector('svg');
        
        if (hotel.is_bookmarked) {
            bookmarkIcon.classList.add('text-red-500');
            bookmarkIcon.setAttribute('fill', 'currentColor');
        } else {
            bookmarkIcon.classList.remove('text-red-500');
            bookmarkIcon.setAttribute('fill', 'none');
        }

        if (csrfToken) {
            bookmarkBtn.addEventListener('click', () => toggleBookmark(hotel.id, bookmarkIcon, csrfToken));
        } else {
            bookmarkBtn.style.display = 'none';
        }

        hotelsGrid.appendChild(card);
    });
}

function toggleBookmark(hotelId, iconElement, csrfToken) {
    fetch(`/bookmark/toggle/${hotelId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 403) {
                alert('Please log in to bookmark hotels.');
                window.location.href = '/login/';
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'added') {
            iconElement.classList.add('text-red-500');
            iconElement.setAttribute('fill', 'currentColor');
        } else if (data.status === 'removed') {
            iconElement.classList.remove('text-red-500');
            iconElement.setAttribute('fill', 'none');
        }
    })
    .catch(error => {
        console.error('Error toggling bookmark:', error);
        alert('Failed to toggle bookmark. Please try again.');
    });
}

// Initialize polling when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Get taskId from the script tag's data attribute, or fallback to direct template variable
    // This is a more robust way to pass context from Django to external JS files.
    const scriptTag = document.querySelector('script[src*="poll.js"]');
    const pageTaskId = scriptTag ? scriptTag.dataset.taskId : "{{ task_id }}";

    if (pageTaskId && pageTaskId !== 'None') {
        startPolling(
            `/hotels/status/${pageTaskId}/`,
            resultsContainer,
            loadingIndicator,
            noResultsMessage,
            hotelCardTemplate,
            csrfToken
        );
    } else {
        loadingIndicator.classList.add('hidden');
        noResultsMessage.classList.remove('hidden');
    }
});
