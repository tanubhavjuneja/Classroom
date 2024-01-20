document.addEventListener('DOMContentLoaded', function () {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
            var username = response.username;
            console.log('Username:', username);
            document.getElementById('usernameLabel').textContent = username;
        }
    };
    xhr.open('GET', '/get_username', true);
    xhr.send();
});
function navigateTo(extension) {
    var url = '/' + extension;
    window.location.href = url;
    console.log('Navigating to:', extension);
}