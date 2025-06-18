document.getElementById('add-attachment-btn').addEventListener('click', function() {
    document.getElementById('attachment-input').click();
});

const searchInput = document.querySelector('.search-input');
const searchMicSpan = document.getElementById('search-mic');
const searchMic = searchMicSpan.querySelector('i');
const chatArea = document.getElementById('chat-area');
const greetingSection = document.getElementById('greeting-section');

let greeted = false;

function sendMessage() {
    const msg = searchInput.value.trim();
    if (!msg) return;

    // Hide greeting and show chat after first message
    if (!greeted) {
        greetingSection.style.display = 'none';
        chatArea.style.display = 'flex';
        greeted = true;
    }

    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.innerHTML = `<div class="bubble user" tabindex="-1">${msg}</div>`;
    chatArea.appendChild(userMsg);

    // Add bot reply "Hi"
    setTimeout(() => {
        const botMsg = document.createElement('div');
        botMsg.className = 'chat-message bot';
        botMsg.innerHTML = `<div class="bubble bot" tabindex="-1">Hi</div>`;
        chatArea.appendChild(botMsg);
        chatArea.scrollTop = chatArea.scrollHeight;
    }, 400);

    // Auto-scroll to latest message and focus last bubble
    setTimeout(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    }, 0);

    searchInput.value = '';
    searchMic.classList.remove('fa-paper-plane');
    searchMic.classList.add('fa-microphone');
}

searchInput.addEventListener('input', function() {
    if (searchInput.value.trim().length > 0) {
        searchMic.classList.remove('fa-microphone');
        searchMic.classList.add('fa-paper-plane');
    } else {
        searchMic.classList.remove('fa-paper-plane');
        searchMic.classList.add('fa-microphone');
    }
});

searchMicSpan.addEventListener('click', function() {
    if (searchMic.classList.contains('fa-paper-plane')) {
        sendMessage();
    }
});

searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && searchInput.value.trim().length > 0) {
        sendMessage();
    }
});

// Always keep chat scrolled to bottom on page load/resize
window.addEventListener('load', () => {
    chatArea.scrollTop = chatArea.scrollHeight;
});
window.addEventListener('resize', () => {
    chatArea.scrollTop = chatArea.scrollHeight;
});