/* Real-Time Validation and Password Strength Indicator */
document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.querySelector('form');
    if (signupForm) {
        const usernameInput = document.getElementById('id_username');
        const emailInput = document.getElementById('id_email');
        const password1Input = document.getElementById('id_password1');
        const password2Input = document.getElementById('id_password2');
        const strengthBar = document.getElementById('password-strength-bar');

        // Function to validate email format
        const validateEmail = (email) => {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(String(email).toLowerCase());
        };

        // Real-time Email Validation
        emailInput.addEventListener('input', () => {
            const errorDiv = emailInput.parentElement.querySelector('.error-message');
            if (!validateEmail(emailInput.value)) {
                emailInput.classList.add('invalid');
                if (!errorDiv) {
                    const error = document.createElement('div');
                    error.className = 'error-message';
                    error.innerText = 'Please enter a valid email address.';
                    emailInput.parentElement.appendChild(error);
                }
            } else {
                emailInput.classList.remove('invalid');
                if (errorDiv) {
                    errorDiv.remove();
                }
            }
        });

        // Real-time Password Matching
        password2Input.addEventListener('input', () => {
            const errorDiv = password2Input.parentElement.querySelector('.error-message');
            if (password1Input.value !== password2Input.value) {
                password2Input.classList.add('invalid');
                if (!errorDiv) {
                    const error = document.createElement('div');
                    error.className = 'error-message';
                    error.innerText = 'Passwords do not match.';
                    password2Input.parentElement.appendChild(error);
                }
            } else {
                password2Input.classList.remove('invalid');
                if (errorDiv) {
                    errorDiv.remove();
                }
            }
        });

        // Password Strength Indicator
        if (strengthBar) {
            password1Input.addEventListener('input', () => {
                const val = password1Input.value;
                let strength = 0;

                // Simple password strength logic
                if (val.length >= 8) strength += 1;
                if (/[A-Z]/.test(val)) strength += 1;
                if (/[0-9]/.test(val)) strength += 1;
                if (/[^A-Za-z0-9]/.test(val)) strength += 1;

                // Update strength bar
                const percentage = (strength / 4) * 100;
                strengthBar.style.width = `${percentage}%`;

                // Update strength bar color
                if (percentage === 100) {
                    strengthBar.style.backgroundColor = '#4caf50'; /* Green */
                } else if (percentage >= 75) {
                    strengthBar.style.backgroundColor = '#ff9800'; /* Orange */
                } else if (percentage >= 50) {
                    strengthBar.style.backgroundColor = '#ffc107'; /* Amber */
                } else {
                    strengthBar.style.backgroundColor = '#d8000c'; /* Red */
                }
            });
        }
    }
});