var currentLanguage = 'html';
var textarea = document.getElementById('code');
var lineNumbersContainer = document.querySelector('.line-numbers');
textarea.addEventListener('input', updateLineNumbers);
textarea.addEventListener('scroll', function () {
    lineNumbersContainer.scrollTop = this.scrollTop;
});
function updateLineNumbers() {
    var lines = textarea.value.split('\n');
    var lineNumbersHTML = '';
    var totalLines = Math.max(lines.length, 100);
    for (var i = 1; i <= totalLines; i++) {
        lineNumbersHTML += '<div class="line-number">' + i + '</div>';
    }
    lineNumbersContainer.innerHTML = lineNumbersHTML;
}
updateLineNumbers();
function switchLanguage(language) {
    saveToFile(currentLanguage);
    currentLanguage = language;
    loadFromFile(currentLanguage);
    setPlaceholder();
}
function setPlaceholder() {
    var placeholderText = 'Enter ' + currentLanguage.toUpperCase() + ' code...';
    document.getElementById('code').placeholder = placeholderText;
}
setPlaceholder();
function saveToFile(language) {
    var code = document.getElementById('code').value;
    if (code.trim() !== '') {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 && xhr.status == 200) {
                document.getElementById('code').value = '';
            }
        };
        xhr.open('POST', '/save', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.send('language=' + language + '&code=' + encodeURIComponent(code));
    }
}
function loadFromFile(language) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            document.getElementById('code').value = xhr.responseText;
        }
    };
    xhr.open('GET', '/load?language=' + language, true);
    xhr.send();
}
function renderCode() {
    saveToFile(currentLanguage);
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            var newTab = window.open();
            newTab.document.open();
            newTab.document.write(xhr.responseText);
            newTab.document.close();
        }
    };
    xhr.open('GET', '/render', true);
    xhr.send();
}
document.getElementById('code').addEventListener('input', function () {
    var code = this.value.trim();
    if (code === '') {
        setPlaceholder();
    } else {
        this.placeholder = '';
    }
});
loadFromFile(currentLanguage);