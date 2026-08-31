let deferredPrompt = null;


window.addEventListener(
    "beforeinstallprompt",
    function (event) {

        event.preventDefault();

        deferredPrompt = event;

    }
);


function installApp() {

    if (!deferredPrompt) {

        alert(
            "Install option is not available yet. " +
            "Open the browser menu and choose Install App."
        );

        return;
    }


    deferredPrompt.prompt();

    deferredPrompt.userChoice.then(function () {

        deferredPrompt = null;

    });

}


function toggleSidebar() {

    const sidebar =
        document.querySelector(".sidebar");

    sidebar.classList.toggle("open");

}


function selectTransactionType(type, button) {

    document
        .querySelectorAll(".type-button")
        .forEach(function (item) {

            item.classList.remove("selected");

        });


    button.classList.add("selected");


    const input =
        document.getElementById("transaction_type");


    if (input) {

        input.value = type;

    }

}


function selectPayment(method, button) {

    document
        .querySelectorAll(".payment-buttons button")
        .forEach(function (item) {

            item.classList.remove("selected");

        });


    button.classList.add("selected");


    const input =
        document.getElementById("payment_method");


    if (input) {

        input.value = method;

    }

}


function toggleDarkMode() {

    const enabled =
        document.getElementById("darkModeToggle").checked;


    if (enabled) {

        document.body.classList.add("dark-mode");

        localStorage.setItem(
            "darkMode",
            "true"
        );

    } else {

        document.body.classList.remove("dark-mode");

        localStorage.setItem(
            "darkMode",
            "false"
        );

    }

}


document.addEventListener(
    "DOMContentLoaded",
    function () {

        const darkMode =
            localStorage.getItem("darkMode");


        if (darkMode === "true") {

            document.body.classList.add(
                "dark-mode"
            );


            const toggle =
                document.getElementById(
                    "darkModeToggle"
                );


            if (toggle) {

                toggle.checked = true;

            }

        }

    }
);