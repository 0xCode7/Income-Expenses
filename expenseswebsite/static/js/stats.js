const pathName = window.location.pathname;
console.log(pathName);


const renderChart = (data, labels) => {
    const ctx = document.getElementById('myChart');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                label: 'Expenses for the last 6 months',
                data: data,
                backgroundColor: [
                    'rgba(255, 120, 250, 0.5)',
                    'rgba(200, 50, 30, 0.5)',
                    'rgba(200, 150, 120, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                    'rgba(255, 159, 64, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {

                title: {
                    display: true,
                    text: 'Expenses by category',
                    font: {
                        size: 20,
                        weight: '600'
                    }
                }
            }
        }
    });

}

function getExpense () {
    fetch('/expense-summary')
        .then(res => res.json())
        .then(expenses => {
            const categoryData = expenses.category_data;
            const [labels, data] = [
                Object.keys(categoryData),
                Object.values(categoryData)
            ];

            renderChart(data, labels);
        })
}

document.onload = getExpense();