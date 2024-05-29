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
        
        if (!validateEmail(email)) {
            alert('Email must end with @nucleusteq.com');
            return;
        }

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
                console.log(response.json,  "json response")
                const user = await fetch('http://127.0.0.1:8000/get_user/'+email)
                const data = await user.json();
                console.log(data.is_admin);
                    // Assuming the response contains the username and other details
                    sessionStorage.setItem('user', JSON.stringify(data));
                   // sessionStorage.setItem('username', password);


                // const subordinates_response = await fetch('http://127.0.0.1:8000/get_subordinates/'+id)
                // const subordinates = await subordinates_response.json();
                // console.log(subordinates);
                //     // Assuming the response contains the username and other details
                //     sessionStorage.setItem('user', JSON.stringify(data));
                //     // sessionStorage.setItem('username', password);
                
            
            if (data.is_admin){
                window.location.href = 'http://127.0.0.1:5500/dashboard.html'; 
            }

            else {
                window.location.href = 'http://127.0.0.1:5500/manager_dashboard.html';
            }
                 
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
       
        const id = null;
        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const department = document.getElementById('registerDepartment').value;
        const role = document.getElementById('registerRole').value;
        const is_admin = false;
        const managerId = null;
        

        if (!validateEmail(email)) {
            alert('Email must end with @nucleusteq.com');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    
                    username:name,
                    email: email,
                    password: password,
                    role: role,
                    department: department,
                    is_admin: is_admin,
                    manager_id: managerId
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

    function validateEmail(email) {
        return email.endsWith('@nucleusteq.com');
    }
});

var passwordInput = document.getElementById("registerPassword");
    var passwordErrorMessage = document.getElementById("passwordErrorMessage");

    passwordInput.addEventListener("input", function() {
        var password = passwordInput.value;
        var errorMessage = '';

        // Reset the style
        passwordInput.classList.remove("invalid");

        if (password.length < 8) {
            errorMessage = "Password must be at least 8 characters long.";
        } else if (!/\d/.test(password)) {
            errorMessage = "Password must contain at least one numeric character.";
        } else if (!/[!@#$%^&*]/.test(password)) {
            errorMessage = "Password must contain at least one special character.";
        } else if (!/[a-z]/.test(password) || !/[A-Z]/.test(password)) {
            errorMessage = "Password must contain both uppercase and lowercase letters.";
        }

        if (errorMessage !== '') {
            passwordInput.classList.add("invalid");
            passwordErrorMessage.textContent = errorMessage;
            passwordErrorMessage.style.display = "block";
        } else {
            passwordErrorMessage.textContent = '';
            passwordErrorMessage.style.display = "none";
        }
    });

    document.addEventListener('DOMContentLoaded', async function () {
        const registerDepartmentSelect = document.getElementById('registerDepartment');
    
        try {
            // Fetch department data from the backend API
            const response = await fetch('http://127.0.0.1:8000/departments/');
            const departments = await response.json();
    
            // Populate the dropdown select element with department options
            departments.forEach(department => {
                const option = document.createElement('option');
                option.value = department.dept_name; // Set the value to department ID
                option.textContent = department.dept_name; // Set the display text to department name
                registerDepartmentSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching department data:', error);
        }
    });
    


     
