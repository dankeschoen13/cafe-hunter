/**
 * Initializes the page once the DOM is fully loaded.
 */
document.addEventListener('DOMContentLoaded', initializePage);

/**
 * Sets up event listeners for the primary interactive elements on the search page,
 * including the main search form, filter toggle switches, and the pagination button.
 */
function initializePage() {
    console.log("DOM loaded, initializing page...");

    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }

    // Attaches eventlisteners for each filter toggles. Watching: change
    const filterToggles = document.querySelectorAll('.filter-toggle');
    filterToggles.forEach(toggle => {
        toggle.addEventListener('change', handleSearchSubmit);
    });

    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreButton)
    }
}

/**
 * Handles the search submission and filter toggle events.
 * Constructs a URL query string based on the current inputs, pushes the new URL
 * to the browser's history state without reloading, updates the active filter UI badges,
 * and triggers the AJAX fetch for filtered cafés.
 *
 * @param {Event} [event] - The DOM event triggered by form submission or toggle change.
 */
function handleSearchSubmit(event) {
    if (event) event.preventDefault();
    
    const searchInput = document.getElementById('searchInput');
    const keyword = searchInput ? searchInput.value : '';

    const params = new URLSearchParams();
    // Constructs URL search params based on current inputs.
    // INPUTS: q, wifi, sockets, calls and toilet

    if (keyword) params.append('q', keyword);
    if (document.getElementById('wifiToggle')?.checked) params.append('wifi', 'true');
    if (document.getElementById('socketsToggle')?.checked) params.append('sockets', 'true');
    if (document.getElementById('callsToggle')?.checked) params.append('calls', 'true');
    if (document.getElementById('toiletToggle')?.checked) params.append('toilet', 'true');

    // Converts search params into concatenated string and
    // push the URL to browser's address bar
    const queryString = params.toString();
    const newUrl = `${window.location.pathname}?${queryString}`;
    window.history.pushState({ path: newUrl }, '', newUrl);

    // Handle the UI state. If any of the filters are checked, the active filters
    // section should appear showing the corresponding filter's badge.
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

/**
 * Fetches the filtered café results from the server via AJAX and updates the DOM.
 * Also manages the visibility and state of the "Load More" pagination button
 * based on the number of results returned.
 *
 * @param {string} queryString - The formatted URL query string containing search parameters.
 */
function fetchFilteredCafes(queryString) {
    const resultsDiv = document.getElementById('results');

    // Display loading spinner while fetching
    resultsDiv.innerHTML = '<div class="text-center mt-4"><div class="spinner-border text-primary"></div></div>';

    fetch(`/search?${queryString}`, {
        headers: { 'X-Requested-With': 'Fetch' }
    })
    .then(response => response.text())
    .then(htmlSnippet => {
        resultsDiv.innerHTML = htmlSnippet;

        // Parse snippet to count returned items
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = htmlSnippet;
        const cardCount = tempDiv.children.length;

        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
            // Assumes a full page consists of 3 cards
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

/**
 * Handles pagination by fetching the next set of café results and appending them
 * to the existing list in the DOM. Updates the button state if no more results exist.
 */
function loadMoreButton() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const resultsDiv = document.getElementById('results');

    // Calculate the next page number to fetch
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
        // Check if the server returned an empty string (no more results)
        if (htmlSnippet.trim() === "") {
            loadMoreBtn.innerText = "No more cafes found";
            loadMoreBtn.disabled = true;
            return;
        }
        // Append the new HTML snippet to the bottom of the results container
        resultsDiv.insertAdjacentHTML('beforeend', htmlSnippet);
        // Update the current page tracker
        loadMoreBtn.setAttribute('data-page', nextPage);
    })
    .catch(error => {
        console.error('Pagination fetch error:', error);
    });
}