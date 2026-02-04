
document.addEventListener('DOMContentLoaded', initializePage);

function initializePage() {
    console.log("DOM loaded, initializing page...");

    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }
}

function handleSearchSubmit(event) {
    event.preventDefault();
    
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value;

    fetchCafes(query);
}

function fetchCafes(query) {
    const resultsDiv = document.getElementById('results');
    
    resultsDiv.innerHTML = `
        <div class="col-12 text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>`;

    fetch(`/api/search?query=${encodeURIComponent(query)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('No cafes found');
            }
            return response.json();
        })
        .then(data => {
            renderCafes(data, resultsDiv);
        })
        .catch(error => {
            resultsDiv.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning" role="alert">
                        No cafes found matching "${query}".
                    </div>
                </div>`;
        });
}

function renderCafes(cafes, container) {
    container.innerHTML = ''; 

    if (cafes.length === 0) {
        container.innerHTML = '<div class="col-12 text-muted">No results found.</div>';
        return;
    }

    cafes.forEach(cafe => {        
        // Simple text cleanup
        let cleanDesc = cafe.description ? cafe.description.replace(/<[^>]*>?/gm, '') : '';
        if (cleanDesc.length > 150) {
            cleanDesc = cleanDesc.substring(0, 150) + '...';
        }
        
        const cafeUrl = `/cafe/${cafe.id}`;

        // Simplified Single-Column Layout
        const listHtml = `
        <div class="col-12 mb-3">
            <div class="d-flex align-items-center p-3 border rounded shadow-sm bg-white">
                
                <img src="/static/${cafe.img_url}" 
                    class="search-result-img me-3 rounded" 
                    alt="${cafe.name}">
                
                <div class="flex-grow-1">
                    <h5 class="mb-1">${cafe.name}</h5>
                    <p class="mb-1 text-secondary small">${cleanDesc}</p>
                    <a href="${cafeUrl}" class="stretched-link text-decoration-none small">View Details</a>
                </div>
            </div>
        </div>`;
        
        container.insertAdjacentHTML('beforeend', listHtml);
    });
}