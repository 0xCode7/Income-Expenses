const showPassword = document.querySelector('.showPassword')
const submitBtn = document.querySelector('.submit-btn')
showPassword.addEventListener("click", () => {
    if (showPassword.textContent === 'SHOW') {
        showPassword.textContent = 'HIDE';
        passwordField.setAttribute('type', 'text')
    } else {
        showPassword.textContent = 'SHOW';
        passwordField.setAttribute('type', 'password')
    }
})
// document.addEventListener("DOMContentLoaded", function () {
//     const deleteBtns = document.querySelectorAll('.delete-btn'); // Select all delete buttons
//     const modalForm = document.getElementById('modalForm');      // Modal form
//
//     deleteBtns.forEach((btn) => {
//         btn.addEventListener('click', () => {
//             const url = btn.getAttribute('data-url');            // Get the data-url attribute
//             if (url) {
//                 modalForm.setAttribute('action', url);          // Update form action dynamically
//             } else {
//                 console.error('data-url is missing for this button'); // Debugging info
//             }
//         });
//     });
// });
