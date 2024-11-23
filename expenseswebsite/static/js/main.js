const showPassword = document.querySelector('.showPassword')
const passwordField = document.querySelector('#passwordField');
const confirmPasswordField = document.querySelector('#confirmPasswordField');
const submitBtn = document.querySelector('.submit-btn')

if (showPassword !== null) {


    showPassword.addEventListener("click", () => {
        if (showPassword.textContent === 'SHOW') {
            showPassword.textContent = 'HIDE';
            passwordField.setAttribute('type', 'text')
            confirmPasswordField.setAttribute('type', 'text')
        } else {
            showPassword.textContent = 'SHOW';
            passwordField.setAttribute('type', 'password')
            confirmPasswordField.setAttribute('type', 'password')
        }
    })
}
