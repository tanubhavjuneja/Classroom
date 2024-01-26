function getUsernameFromServer() {
    fetch('/get_username')
    .then(response => response.json())
    .then(data => {
        const username = data.username;
        if (username) {
            document.getElementById('usernameInput').value = username;
        } else {
            const storedUsername = localStorage.getItem('username');
            if (storedUsername) {
                document.getElementById('usernameInput').value = storedUsername;
            } else {
                const newUsername = prompt('Please enter your username:');
                document.getElementById('usernameInput').value = newUsername;
                localStorage.setItem('username', newUsername);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
getUsernameFromServer();
let userScrolledManually = false; 
function scrollToBottom() {
const chatFrame = document.getElementById('chatFrame');
chatFrame.scrollTop = chatFrame.scrollHeight;
}
const chatFrame = document.getElementById('chatFrame');
chatFrame.addEventListener('scroll', function() {
userScrolledManually = chatFrame.scrollTop + chatFrame.clientHeight < chatFrame.scrollHeight;
});
function fetchMessagesFromServer() {
fetch('/chat/receive')
.then(response => response.json())
.then(data => {
const chatFrame = document.getElementById('chatFrame');
const wasAtBottom = chatFrame.scrollTop + chatFrame.clientHeight >= chatFrame.scrollHeight - 20;
chatFrame.innerHTML = '';
data.messages.forEach(message => {
    appendMessageToChatFrame(message.trim());
});
if (wasAtBottom || !userScrolledManually) {
    scrollToBottom();
}
})
.catch(error => {
console.error('Error fetching messages:', error);
});
}
function appendMessageToChatFrame(message) {
const chatFrame = document.getElementById('chatFrame');
const messageContainer = document.createElement('div');
messageContainer.className = 'messageContainer';
const messageBubble = document.createElement('div');
messageBubble.className = 'messageBubble';
const match = message.match(/^\d+\.\d+\.\d+\.\d+ \(([^)]+)\): (.+)$/);
if (match && match.length === 3) {
const username = match[1];
const content = match[2];
messageBubble.innerText = `${username}: ${content}`;
} else {
messageBubble.innerText = message;
}
messageContainer.appendChild(messageBubble);
chatFrame.appendChild(messageContainer);
}
fetchMessagesFromServer();
function startMessageFetchingScheduler() {
setInterval(() => {
fetchMessagesFromServer();
}, 1000); 
}
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim(); 
    const username = document.getElementById('usernameInput').value;
    if (message !== '') {
        fetch('/chat/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `message=${encodeURIComponent(message)}&username=${encodeURIComponent(username)}`
        })
        .then(() => {
            fetchMessagesFromServer();
            messageInput.value = '';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}
document.getElementById('messageInput').addEventListener('keydown', function(event) {
if (event.key === 'Enter') {
event.preventDefault();
sendMessage(); 
}
});
fetchMessagesFromServer();
startMessageFetchingScheduler();