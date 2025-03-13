document.addEventListener("DOMContentLoaded", function () {
    let page = 1;
    const newsContainer = document.getElementById("news-container");
    const loadingDiv = document.getElementById("loading");

    function loadNews() {
        loadingDiv.style.display = "block";
        fetch(`/api/news/?page=${page}`)
            .then(response => response.json())
            .then(data => {
                data.results.forEach(news => {
                    const newsElement = document.createElement("div");
                    newsElement.classList.add("card", "mb-3");
                    newsElement.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">${news.title}</h5>
                            <p class="card-text">${news.text.substring(0, 150)}...</p>
                            <a href="/news/${news.id}/" class="btn btn-primary">Read More</a>
                        </div>
                    `;
                    newsContainer.appendChild(newsElement);
                });
                loadingDiv.style.display = "none";
                page++;
            })
            .catch(error => console.error("Error loading news:", error));
    }

    window.addEventListener("scroll", () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            loadNews();
        }
    });

    loadNews();
});
