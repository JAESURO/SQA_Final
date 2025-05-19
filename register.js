document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("userId")) {
      window.location.href = "index.html"
    }
    const registerForm = document.getElementById("registerForm")
  
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault()
  
      const email = document.getElementById("email").value
      const password = document.getElementById("password").value
      const confirmPassword = document.getElementById("confirmPassword").value
      if (!email || !password || !confirmPassword) {
        alert("Please fill in all fields")
        return
      }
  
      if (password !== confirmPassword) {
        alert("Passwords do not match")
        return
      }
  
      try {
        const response = await fetch('http://localhost:3000/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert('Registration successful! Please login.');
          window.location.href = 'login.html';
        } else {
          alert(data.error);
        }
        
      } catch (error) {
        alert("Error connecting to server")
        console.error("Registration error:", error)
      }
    })
  })
