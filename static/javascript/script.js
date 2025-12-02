
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

    cafes.forEach(cafe => {        
        let cleanDesc = cafe.description ? cafe.description.replace(/<[^>]*>?/gm, '') : '';
        if (cleanDesc.length > 200) {
            cleanDesc = cleanDesc.substring(0, 200) + '...';
        }
        
        const cafeUrl = `/cafe/${cafe.id}`;

        const cardHtml = `
        <div class="col-md-6">
            <div class="row g-0 border rounded overflow-hidden flex-md-row mb-4 shadow-sm h-md-250 position-relative">
                <div class="col p-4 d-flex flex-column position-static">
                    <p class="mb-2 loc">${cafe.location}</p>
                    <h3 class="mb-0">${cafe.name}</h3>
                    <p class="card-text mt-auto">${cleanDesc}</p>
                    <a href="${cafeUrl}" class="icon-link gap-1 icon-link-hover stretched-link">
                        Continue reading
                        <svg class="bi" aria-hidden="true"><use xlink:href="#chevron-right"></use></svg>
                    </a>
                </div>
                <div class="col-auto d-none d-lg-block">
                    <img src="${cafe.img_url}" class="bd-placeholder-img" height="250" style="object-fit: cover;" role="img" width="200" alt="${cafe.name}" />
                </div>
            </div>
        </div>`;
        
        container.insertAdjacentHTML('beforeend', cardHtml);
    });
}