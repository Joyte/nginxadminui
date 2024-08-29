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

class AlertManager {
    init() {
        this.container = $("#alerts")[0];
    }

    alert(header, message, options) {
        if (typeof options != "object") {
            options = {};
        }

        let {
            duration = 5000,
            color = "var(--success-color)",
            text = "var(--text-color)",
        } = options;

        var alert = document.createElement("article");
        var alertTitle = document.createElement("h3");
        var alertMessage = document.createElement("p");

        alertTitle.innerHTML = header;
        alertMessage.innerHTML = message;

        // Colors for ::after
        alert.style.setProperty("--progressbar-color", color);
        alert.style.setProperty("--progressbar-width", "0%");
        alertTitle.style.color = text;
        alertMessage.style.color = text;

        alert.appendChild(alertTitle);
        alert.appendChild(alertMessage);

        // Use :after to create a loading bar to show how long the alert will be displayed

        this.container.prepend(alert);

        function updateProgress() {
            var width = parseInt(
                alert.style.getPropertyValue("--progressbar-width")
            );
            width = width + 1;
            alert.style.setProperty("--progressbar-width", width + "%");
            if (width < 100) {
                setTimeout(updateProgress, duration / 100);
            } else {
                alert.remove();
            }
        }

        updateProgress();
    }
}

const spaManager = new SinglePageApplicationManager();
const alertManager = new AlertManager();
document.addEventListener("DOMContentLoaded", function () {
    spaManager.init();
    alertManager.init();
});
