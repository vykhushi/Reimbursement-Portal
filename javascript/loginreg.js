document.addEventListener('DOMContentLoaded', function() {
    const loginContent = document.getElementById('loginContent');
    const registerContent = document.getElementById('registerContent');
    const showRegisterLink = document.getElementById('showRegister');
    const showLoginLink = document.getElementById('showLogin');

    // Function to show login form and hide register form
    function showLoginForm() {
        loginContent.style.display = 'block';
        registerContent.style.display = 'none';
    }

    // Function to show register form and hide login form
    function showRegisterForm() {
        loginContent.style.display = 'none';
        registerContent.style.display = 'block';
    }

    // Add event listener for "Register here" link to show registration form
    showRegisterLink.addEventListener('click', function(event) {
        event.preventDefault();
        showRegisterForm();
    });

    // Add event listener for "Login here" link to show login form
    showLoginLink.addEventListener('click', function(event) {
        event.preventDefault();
        showLoginForm();
    });

    // Show login form by default
    showLoginForm();

    // Function to handle login form submission
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        console.log(email, password);

        try {
            const response = await fetch('http://127.0.0.1:8000/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            if (response.ok) {
                window.location.href = 'http://127.0.0.1:5500/dashboard.html'; 
            } else {
                const data = await response.json();
                alert(data.detail); 
            }
        } catch (error) {
            // console.error('Error:', error);
        }
    });

    
    const registerForm = document.getElementById('registerForm');
    registerForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const department = document.getElementById('registerDepartment').value;
        const role = document.getElementById('registerRole').value;

        try {
            const response = await fetch('http://127.0.0.1:8000/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username:  name,
                    email: email,
                    password: password,
                    role: role,
                    department: department
                })
            });

            if (response.ok) {
                alert('Registration successful. Please login.');
                showLoginForm(); 
            } else {
                const data = await response.json();
                alert(data.detail); 
            }
        } catch (error) {
            // console.error('Error:', error);
        }
    });
});
    


     
