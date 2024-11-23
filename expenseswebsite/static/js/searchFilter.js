const searchInput = document.getElementById('searchInput');
const getCSRFToken = () => document.querySelector('[name=csrfmiddlewaretoken]').value;
const pagination = document.querySelector('.pagination');
const pathName = window.location.pathname;
const prefix = pathName === '/income/' ? 'income' : 'expense';
const tableBody = document.getElementById(`${prefix}sTableBody`);
const mainTableContent = tableBody.innerHTML;

searchInput.addEventListener('keyup', function () {
    const query = searchInput.value;

    fetch(`${prefix === 'income' ? '/income/search/' : '/search/'}`, {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({searchText: query}),
        method: 'POST',
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            let rows = '';

            if (query.length === 0) {
                // Reset to the original content when search input is empty
                tableBody.innerHTML = mainTableContent;
                pagination.style.display = 'flex';
                return; // Exit early to avoid overwriting table with rows
            }

            else if (data.length > 0) {
                pagination.style.display = 'none';
                data.forEach(item => {
                    rows += `
                    <tr>
                        <td>${item.amount}</td>
                        <td>${prefix == 'income' ? item.source : item.category}</td>
                        <td>${item.description}</td>
                        <td>${item.date}</td>
                        <td>
                            <a href="/update-${prefix}/${item.id}" class="btn btn-sm btn-primary">Edit</a>
                            <a href="/delete-${prefix}/${item.id}" class="btn btn-sm btn-danger">Delete</a>
                        </td>
                    </tr>`;
                });
            } else {
                rows = `
                <tr>
                    <td colspan="5">No items found</td>
                </tr>`;
            }

            // Only update the table if there's new content
            tableBody.innerHTML = rows;
        })
        .catch(error => {
            console.error('There was an error with the fetch operation:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">An error occurred while fetching data. Please try again.</td>
                </tr>`;
        });
});
