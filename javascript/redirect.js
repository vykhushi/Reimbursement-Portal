document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');

    // Event listener for register form submission
    registerForm.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent default form submission

        // Get form input values
        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const department = document.getElementById('registerDepartment').value;
        const role = document.getElementById('registerRole').value;

        // Simulate registration process (replace with actual registration API call)
        const registrationSuccess = await registerUser(name, email, password, department, role);

        if (registrationSuccess) {
            // Redirect to dashboard page after successful registration
            window.location.href = 'dashboard.html';
        } else {
            alert('Registration failed. Please try again.'); // Display error message
        }
    });

    // Function to simulate user registration (replace with actual API call)
    async function registerUser(name, email, password, department, role) {
        
        return true; // Change to false if registration fails
    }
});
