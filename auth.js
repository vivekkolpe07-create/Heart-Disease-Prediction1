
// LOGIN FORM
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const message = document.getElementById("message");
        message.textContent = "Please wait...";

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                window.location.href = data.redirect || "/";
            } else {
                message.textContent = data.error || "Login failed";
            }
        } catch (error) {
            message.textContent = "Server connection failed!";
        }
    });
}


// SIGNUP FORM
const signupForm = document.getElementById("signupForm");

if (signupForm) {
    signupForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const message = document.getElementById("message");
        message.textContent = "Creating account...";

        const name = document.getElementById("name").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("/api/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ name, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                window.location.href = data.redirect || "/";
            } else {
                message.textContent = data.error || "Signup failed";
            }
        } catch (error) {
            message.textContent = "Server connection failed!";
        }
    });
}

// LOGOUT FUNCTION
const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {
    logoutBtn.addEventListener("click", async function () {
        try {
            const response = await fetch("/api/logout", {
                method: "POST"
            });

            if (response.ok) {
                window.location.href = "/login";
            } else {
                alert("Logout failed. Please try again.");
            }
        } catch (error) {
            alert("Server connection failed!");
        }
    });
}
