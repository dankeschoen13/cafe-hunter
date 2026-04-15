document.addEventListener("DOMContentLoaded", initSearchWidget);

function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function initSearchWidget() {
    const header = document.getElementById('mainHeader');
    const searchWidget = document.getElementById('searchWidget');
    const searchToggleBtn = document.getElementById('searchToggleBtn');
    const searchInput = document.getElementById('quickSearchInput');
    const dropdown = document.getElementById('searchDropdown');
    const resultsContainer = document.getElementById('quickSearchResults');
    const viewAllBtn = document.getElementById('viewAllResultsBtn');

    searchToggleBtn.addEventListener('click', (e) => {
        e.preventDefault();

        searchWidget.classList.toggle('active');
        header.classList.toggle('header-search-mode');
        
        if (searchWidget.classList.contains('active')) {
            searchInput.focus();
        } else {
            dropdown.classList.add('d-none');
            searchInput.value = '';
        }
    });

    document.addEventListener('click', (e) => {
        if (!searchWidget.contains(e.target) && !dropdown.contains(e.target)) {
            searchWidget.classList.remove('active');
            header.classList.remove('header-search-mode');
            dropdown.classList.add('d-none');
        }
    });

    const performSearch = async (e) => {
        const query = e.target.value.trim();

        if (!query) {
            dropdown.classList.add('d-none');
            return;
        }

        dropdown.classList.remove('d-none');
        viewAllBtn.href = `/search?q=${encodeURIComponent(query)}`;
        viewAllBtn.classList.remove('d-none');

        resultsContainer.innerHTML = '<div class="text-muted text-center small py-3">Searching...</div>';

        try {
            const response = await fetch(`/api/cafes/search?q=${encodeURIComponent(query)}`);
            const cafes = await response.json();

            resultsContainer.innerHTML = '';

            if (cafes.length === 0) {
                resultsContainer.innerHTML = `<div class="text-muted text-center small py-3">No cafes found for "${query}"</div>`;
                return;
            }

            const fragment = document.createDocumentFragment();
            cafes.forEach(cafe => {
                const a = document.createElement('a');
                a.href = `/show-cafe/id=${cafe.id}`; 
                a.className = 'list-group-item list-group-item-action border-0 px-3 py-2';
                a.innerHTML = `
                    <div class="fw-bold text-truncate">${cafe.name}</div>
                    <small><i class="bi bi-geo-alt-fill me-1"></i>${cafe.location}</small>
                `;
                fragment.appendChild(a);
            });
            resultsContainer.appendChild(fragment);

        } catch (error) {
            console.error('Search error:', error);
            resultsContainer.innerHTML = `<div class="text-danger text-center small py-3">Error loading results.</div>`;
        }
    };

    searchInput.addEventListener('input', debounce(performSearch, 300));
}