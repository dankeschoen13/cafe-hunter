document.addEventListener('DOMContentLoaded', initializePage);

function initializePage() {
    console.log("DOM loaded, initializing page...");

    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }

    const filterToggles = document.querySelectorAll('.filter-toggle');
    filterToggles.forEach(toggle => {
        toggle.addEventListener('change', handleSearchSubmit);
    });

    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreButton)
    }
}


function handleSearchSubmit(event) {
    if (event) event.preventDefault();
    
    const searchInput = document.getElementById('searchInput');
    const keyword = searchInput ? searchInput.value : '';

    const params = new URLSearchParams();
    if (keyword) params.append('q', keyword);

    if (document.getElementById('wifiToggle')?.checked) params.append('wifi', 'true');
    if (document.getElementById('socketsToggle')?.checked) params.append('sockets', 'true');
    if (document.getElementById('callsToggle')?.checked) params.append('calls', 'true');
    if (document.getElementById('toiletToggle')?.checked) params.append('toilet', 'true');

    const queryString = params.toString();

    const newUrl = `${window.location.pathname}?${queryString}`;
    window.history.pushState({ path: newUrl }, '', newUrl);


    const isWifi = document.getElementById('wifiToggle')?.checked;
    const isSockets = document.getElementById('socketsToggle')?.checked;
    const isCalls = document.getElementById('callsToggle')?.checked;
    const isToilet = document.getElementById('toiletToggle')?.checked;

    document.getElementById('badge-wifi').classList.toggle('d-none', !isWifi);
    document.getElementById('badge-sockets').classList.toggle('d-none', !isSockets);
    document.getElementById('badge-calls').classList.toggle('d-none', !isCalls);
    document.getElementById('badge-toilet').classList.toggle('d-none', !isToilet);

    const anyChecked = isWifi || isSockets || isCalls || isToilet;
    document.getElementById('activeFiltersBlock').classList.toggle('d-none', !anyChecked);

    fetchFilteredCafes(queryString);
}


function fetchFilteredCafes(queryString) {
    const resultsDiv = document.getElementById('results');
    
    resultsDiv.innerHTML = '<div class="text-center mt-4"><div class="spinner-border text-primary"></div></div>';

    fetch(`/search?${queryString}`, {
        headers: { 'X-Requested-With': 'Fetch' }
    })
    .then(response => response.text())
    .then(htmlSnippet => {
        resultsDiv.innerHTML = htmlSnippet;

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlSnippet;
        const cardCount = tempDiv.children.length;

        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
            if (cardCount === 3) {
                loadMoreBtn.classList.remove('d-none');
                loadMoreBtn.disabled = false;
                loadMoreBtn.innerText = "Load More";
                loadMoreBtn.setAttribute('data-page', 1);
            } else {
                loadMoreBtn.classList.add('d-none');
            }
        }
    })
    .catch(error => {
        resultsDiv.innerHTML = '<div class="alert alert-danger">Error loading cafes.</div>';
    });
}


function loadMoreButton() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const resultsDiv = document.getElementById('results');
    
    let nextPage = parseInt(loadMoreBtn.getAttribute('data-page')) + 1;
    
    
    const urlParams = new URLSearchParams(window.location.search);
    
    urlParams.set('page', nextPage);

    fetch(`/search?${urlParams.toString()}`, {
        headers: {
            'X-Requested-With': 'Fetch' 
        }
    })
    .then(response => response.text())
    .then(htmlSnippet => {
        if (htmlSnippet.trim() === "") {
            loadMoreBtn.innerText = "No more cafes found";
            loadMoreBtn.disabled = true;
            return;
        }

        resultsDiv.insertAdjacentHTML('beforeend', htmlSnippet);
    
        loadMoreBtn.setAttribute('data-page', nextPage);
    });
}