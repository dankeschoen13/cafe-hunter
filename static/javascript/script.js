document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent page reload

    const query = document.getElementById('searchInput').value;

    fetch(`/search_results?q=${encodeURIComponent(query)}`)
        .then(response => response.text())
        .then(html => {
            document.getElementById('results').innerHTML = html;
        });
});