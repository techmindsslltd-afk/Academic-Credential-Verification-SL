
        const { ipcRenderer } = require("electron");
        const form = document.getElementById("form");
        const errorMessage = document.getElementById("error-message");
    
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            const email = form.elements.email.value;
            const password = form.elements.password.value;
            ipcRenderer.send("login", { email, password });
        });
    
        ipcRenderer.on("login-success", (event, token) => {
            localStorage.setItem("token", token);
            window.location.href = "./../app/index.html";
        });
    
        ipcRenderer.on("login-error", (event, message) => {
            errorMessage.innerHTML = message;
            errorMessage.style.display = "block";
        });
          




       const signUpButton = document.getElementById('signUp');
        const signInButton = document.getElementById('signIn');
        const container = document.getElementById('container');

        signUpButton.addEventListener('click', () => {
            container.classList.add('right-panel-active');
        });

        signInButton.addEventListener('click', () => {
            container.classList.remove('right-panel-active');
        });  