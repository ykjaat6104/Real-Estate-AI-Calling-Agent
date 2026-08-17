/* Authentication logic */
"use strict";

const API_BASE = "";

function getAuthToken() {
    return localStorage.getItem("access_token");
}

function requireAuth() {
    if (!getAuthToken()) {
        window.location.href = "/login";
        return false;
    }
    return true;
}

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    window.location.href = "/login";
}

async function login(email, password) {
    const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
    }

    const data = await response.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.setItem("user", JSON.stringify(data.user));

    return data;
}

async function register(userData) {
    const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Registration failed");
    }

    return await response.json();
}

// Login form handler
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const button = e.target.querySelector("button");

    try {
        button.disabled = true;
        button.textContent = "Signing in...";

        await login(email, password);
        window.location.href = "/";
    } catch (err) {
        alert(err.message);
    } finally {
        button.disabled = false;
        button.textContent = "Sign In";
    }
});

// Logout button handler
document.getElementById("logoutBtn")?.addEventListener("click", logout);

// Check auth on page load
if (document.querySelector(".auth-page") === null) {
    requireAuth();
}
