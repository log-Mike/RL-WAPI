document.addEventListener("DOMContentLoaded", function () {
    const userSelect = document.getElementById("column1");
    const networkSelect = document.getElementById("column2");
    const submitButton = document.querySelector("input[type='submit']");
    const tableBody = document.querySelector("table tbody");
    
    submitButton.addEventListener("click", function (event) {
        event.preventDefault();
        const user = userSelect.value;
        const network = networkSelect.value.toLowerCase();

        // Make an AJAX PATCH request to update the record
        fetch("/allocate", {
            method: "PATCH",
            body: new URLSearchParams({ user, network }),
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {    
                    /* 
                        Binary search to find the correct row
                        Case insensitive because SQL default is
                        Assure in app.py that the table
                        is ordered by network:name
                    
                        workaround with no web socket yet
                        
                        if we have to update the html table but the
                        query updated 0 results, it means another
                        admin updated it on their own end
                        
                        if we have don't have to update html table
                        and query updated 0, it means the update
                        didn't happen at all, ie already assigned
                    */
                    
                    let left = 0;
                    let right = tableBody.rows.length - 1;
                    
                    let updated = false;
                    
                    while (left <= right) {
                        const mid = Math.floor((left + right) / 2);
                        const network = tableBody.rows[mid].cells[0].textContent.toLowerCase();
                        if (network === data.network) {
                            // make the update
                            if (tableBody.rows[mid].cells[1].textContent != data.user){
                                tableBody.rows[mid].cells[1].textContent = data.user;
                                tableBody.rows[mid].cells[2].textContent = 'Just now';
                                updated = true;
                            }
                            break;
                        } else if (network < data.network) {
                            left = mid + 1;
                        } else {
                            right = mid - 1;
                        }
                    }
                    
                    let result = "";
                    
                    if(data.num_updated === 0){
                        if (updated){
                            result = "Already assigned by another admin, row updated on your end";
                        }
                        else{
                            result = "No rows updated, either already assigned or an error";
                        }
                    }
                    else if(data.num_updated === 1){
                        result = "Successfully updated";
                    }
                    else{
                        result = "More than one row updated" +
                        " this html table wiil not reflect" +
                        " this, refresh page";
                    }
                    alert(result);
                }
            })
            .catch(error => console.error(error));
    });
});