const CACHE_NAME = "finance-tracker-v1";

const FILES_TO_CACHE = [
    "/",
    "/income",
    "/expenses",
    "/analytics",
    "/search",
    "/settings",
    "/static/style.css"
];


self.addEventListener(
    "install",
    function (event) {

        event.waitUntil(

            caches.open(CACHE_NAME)
                .then(function (cache) {

                    return cache.addAll(
                        FILES_TO_CACHE
                    );

                })

        );

    }
);


self.addEventListener(
    "activate",
    function (event) {

        event.waitUntil(

            caches.keys()
                .then(function (cacheNames) {

                    return Promise.all(

                        cacheNames
                            .filter(function (name) {

                                return name !== CACHE_NAME;

                            })
                            .map(function (name) {

                                return caches.delete(name);

                            })

                    );

                })

        );

    }
);


self.addEventListener(
    "fetch",
    function (event) {

        event.respondWith(

            fetch(event.request)
                .catch(function () {

                    return caches.match(
                        event.request
                    );

                })

        );

    }
);