function submitForm() {
    let formData = $("#login-form").serialize();
    $.ajax({
        type: "POST",
        url: "/login",
        data: formData,
        success: function (response) {
            if (response.success) {
                // Successful login, redirect or perform other actions
                window.location.href = "/home";
            } else {
                // Failed login, display error message
                alert(response.message);
            }
        }
    });
}