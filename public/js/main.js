class LoadingManager {
    constructor() {
        this.loadingCount = 0;
        this.loadingDiv = null;
    }

    isLoading() {
        return this.loadingCount > 0;
    }

    setLoading(loading) {
        if (this.loadingDiv == null) {
            this.loadingDiv = document.createElement("div");
            this.loadingDiv.id = "loadingDiv";
            this.loadingDiv.style.display = "none";
            this.loadingDiv.style.position = "fixed";
            this.loadingDiv.style.top = "0";
            this.loadingDiv.style.left = "0";
            this.loadingDiv.style.width = "100%";
            this.loadingDiv.style.height = "100%";
            this.loadingDiv.style.background = "rgba(0,0,0,0.5)";
            this.loadingDiv.style.zIndex = "999999";
            this.loadingDiv.style.cursor = "wait";

            document.body.appendChild(this.loadingDiv);
        }

        this.loadingCount = this.loadingCount + (loading ? 1 : -1);

        if (this.loadingCount > 0) {
            this.loadingDiv.style.display = "block";
        } else {
            this.loadingDiv.style.display = "none";
        }

        if (this.loadingCount < 0) {
            console.error("Loader count below 0");
            this.loadingCount = 0;
        }
    }
}

class SinglePageApplicationManager {
    constructor() {
        this.loadingManager = new LoadingManager();
        this.currentPage = null;
    }

    setLoading(loading) {
        this.loadingManager.setLoading(loading);
    }

    setCurrentPage(pageName, query) {
        if (this.currentPage) {
            this.currentPage.classList.remove("active");
        }

        this.currentPage = document.querySelector("li[to='" + pageName + "']");
        this.currentPage.classList.add("active");

        // Remove empty query parameters
        for (const key in query) {
            if (query[key] === "") {
                delete query[key];
            }
        }

        const queryString = query
            ? `?${new URLSearchParams(query).toString()}`
            : "";

        window.history.pushState(
            { page: pageName },
            pageName,
            "/page/" + pageName + (queryString.length == 1 ? "" : queryString)
        );

        document.title =
            "Nginx Admin UI - " + $(this.currentPage).attr("display");
    }

    goToPage(pageName, query = {}) {
        // Call the API using Ajax to get the page content and load it into the main content area
        $.ajax({
            url: "/api/page/" + pageName,
            beforeSend: () => {
                this.loadingManager.setLoading(true);
            },
            success: (data) => {
                $(document).off("NAUIPageLoaded");
                $("main").html(data);
                this.setCurrentPage(pageName, query);
                $(document).trigger("NAUIPageLoaded");
            },
            complete: () => {
                this.loadingManager.setLoading(false);
            },
        });
    }

    init() {
        $("#navlist li").on("click", (event) => {
            var to = $(event.target).attr("to");
            if (!to) return;
            if ($(event.target).hasClass("active")) return;
            if ($(event.target).hasClass("disabled")) return;

            this.goToPage(to);
        });

        // Handle back/forward button
        window.onpopstate = (event) => {
            if (event.state) {
                this.goToPage(event.state.page);
            }
        };

        // Load whatever page is in the URL, or default to home
        var pageName = window.location.pathname.split("/").pop();
        if (pageName === "") {
            pageName = "home";
        }

        this.goToPage(
            pageName,
            Object.fromEntries(
                new URLSearchParams(window.location.search).entries()
            )
        );
    }
}

const spaManager = new SinglePageApplicationManager();
document.addEventListener("DOMContentLoaded", function () {
    spaManager.init();
});
