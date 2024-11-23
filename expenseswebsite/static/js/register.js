const usernameField = document.querySelector('#usernameField');
const emailField = document.querySelector('#emailField');
const usernameErrorField = document.querySelector('.usernameErrorField');
const emailErrorField = document.querySelector('.emailErrorField');

if (usernameField) {


    usernameField.addEventListener('keyup', (e) => {
        const usernameValue = e.target.value;
        if (usernameValue.length > 0) {
            fetch('/auth/validate-username', {
                body: JSON.stringify({username: usernameValue}),
                method: 'POST',
            })
                .then((res) => res.json())
                .then((data) => {
                    usernameErrorField.style.display = 'block';
                    if (data.username_error) {
                        submitBtn.setAttribute('disabled', 'disabled');
                        submitBtn.disabled = true;
                        submitBtn.style.cursor = 'not-allowed';
                        usernameField.classList.remove('is-valid');
                        usernameField.classList.add('is-invalid');
                        usernameErrorField.style.color = 'red';
                        usernameErrorField.innerHTML = `<p>${data.username_error}</p>`;
                    } else {
                        usernameField.classList.remove('is-invalid');
                        usernameField.classList.add('is-valid');
                        usernameErrorField.style.color = 'green';
                        usernameErrorField.innerHTML = "<p>Username is available</p>";

                    }
                })
        } else {
            usernameField.classList.remove('is-valid', 'is-invalid');
            usernameErrorField.style.display = 'none';
        }
    });
}

if (emailField) {

    emailField.addEventListener('keyup', (e) => {
        const emailValue = e.target.value;
        if (emailValue.length > 0) {
            fetch('/auth/validate-email', {
                body: JSON.stringify({email: emailValue}),
                method: 'POST',
            })
                .then((res) => res.json())
                .then((data) => {
                    emailErrorField.style.display = 'block'
                    if (data.email_error) {
                        submitBtn.setAttribute('disabled', 'disabled')
                        submitBtn.disabled = true
                        submitBtn.style.cursor = 'not-allowed'
                        emailField.classList.remove('is-valid')
                        emailField.classList.add('is-invalid')
                        emailErrorField.style.color = 'red'
                        emailErrorField.innerHTML = `<p>${data.email_error}</p>`
                    } else {
                        submitBtn.removeAttribute('disabled')
                        submitBtn.disabled = false
                        submitBtn.style.cursor = 'pointer'
                        emailField.classList.remove('is-invalid')
                        emailField.classList.add('is-valid')
                        emailErrorField.style.color = 'green'
                        emailErrorField.innerHTML = `<p>Email is valid</p>`
                    }
                })
        } else {
            emailField.classList.remove('is-valid', 'is-invalid');
            emailErrorField.style.display = 'none';
        }
    })
}
