var currentLanguage = 'html';
var textarea = document.getElementById('code');
let counter = 0;
let counterHistory = [0];
let historyIndex = 0;
const counterBtn = document.getElementById('counterBtn');
const counterValue = document.getElementById('counterValue');
loadFromFile(currentLanguage);
setPlaceholder();
counterBtn.addEventListener('click', () => {
    counter++;
    counterValue.textContent = `Counter: ${counter}`;
    addToHistory(counter);
});
document.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.key === 'z') {
        undo();
    } else if (event.ctrlKey && event.key === 'y') {
        redo();
    }
});
function addToHistory(value) {
    counterHistory.splice(historyIndex + 1);
    counterHistory.push(value);
    historyIndex = counterHistory.length - 1;
}
function undo() {
    if (historyIndex > 0) {
        historyIndex--;
        counter = counterHistory[historyIndex];
        updateCounter();
    }
}
function redo() {
    if (historyIndex < counterHistory.length - 1) {
        historyIndex++;
        counter = counterHistory[historyIndex];
        updateCounter();
    }
}
function updateCounter() {
    counterValue.textContent = `Counter: ${counter}`;
}
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
    loadFromFile(currentLanguage);
    setPlaceholder();
}
document.getElementById('code').addEventListener('input', function () {
    var code = this.value.trim();
    if (code === '') {
        setPlaceholder();
    } else {
        this.placeholder = '';
    }
});
