document.addEventListener('DOMContentLoaded', function () {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var response = JSON.parse(xhr.responseText);
            var username = response.username;
            document.getElementById('usernameLabel').textContent = username;

            var files = response.files;
            displayFiles(files);
        }
    };
    xhr.open('GET', '/list_files?dir=Books', true);
    xhr.send();
});
function displayFiles(files) {
    var container = document.getElementById('fileContainer');
    container.innerHTML = ''; // Clear previous content

    files.forEach(function (file) {
        var card = document.createElement('div');
        card.className = 'file-card';
        var downloadLink = document.createElement('a');
        downloadLink.href = '/download/' + encodeURIComponent(file);
        downloadLink.style.cursor = 'pointer';
        var fileName = document.createElement('div');
        fileName.className = 'file-name';
        fileName.textContent = file;
        downloadLink.appendChild(fileName);
        downloadLink.appendChild(document.createElement('br')); 
        card.appendChild(downloadLink);
        container.appendChild(card);
    });
}