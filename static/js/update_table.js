document.addEventListener("DOMContentLoaded", function () {
    const userSelect = document.getElementById("column1");
    const networkSelect = document.getElementById("column2");
    const submitButton = document.querySelector("input[type='submit']");
    const tableBody = document.querySelector("table tbody");
    
    submitButton.addEventListener("click", function (event) {
        event.preventDefault();
        const user = userSelect.value;
        const network = networkSelect.value;

        // Make an AJAX POST request to update the record
        fetch("/allocate/f", {
            method: "POST",
            body: new URLSearchParams({ user, network }),
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Binary search to find the correct row
                    // Asure in app.py that the table
                    // is ordered by network:name
                    let left = 0;
                    let right = tableBody.rows.length - 1;

                    while (left <= right) {
                        const mid = Math.floor((left + right) / 2);
                        const networkName = tableBody.rows[mid].cells[0].textContent;

                        if (networkName === data.networkName) {
                            // make the update
                            tableBody.rows[mid].cells[1].textContent = data.updatedUser;
                            break;
                        } else if (networkName < data.networkName) {
                            left = mid + 1;
                        } else {
                            right = mid - 1;
                        }
                    }
                }
            })
            .catch(error => console.error(error));
    });
});