document.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("userId")) {
    window.location.href = "index.html"
  }

  const loginForm = document.getElementById("loginForm")

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault()

    const email = document.getElementById("email").value
    const password = document.getElementById("password").value
    const rememberMe = document.getElementById("rememberMe").checked
    if (!email || !password) {
      alert("Please enter both email and password")
      return
    }

    try {
      const response = await fetch('http://localhost:3000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("userId", data.userId);
        window.location.href = "index.html";
      } else {
        alert(data.error || "Login failed");
      }
    } catch (error) {
      console.error('Login error:', error);
      alert("Error connecting to server");
    }
  })

  const registerLink = document.getElementById("registerLink")

  registerLink.addEventListener("click", (e) => {
    e.preventDefault()
    window.location.href = "register.html"
  })
})