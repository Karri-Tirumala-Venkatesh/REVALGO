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

    // Show a loading bubble for the assistant
    const botMsg = document.createElement('div');
    botMsg.className = 'chat-message bot';
    botMsg.innerHTML = `<div class="bubble bot" tabindex="-1">...</div>`;
    chatArea.appendChild(botMsg);
    chatArea.scrollTop = chatArea.scrollHeight;

    // Send to Gemini API
    fetch('/shopping/gemini-chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN // <-- ADDED THIS LINE!
        },
        body: JSON.stringify({message: msg})
    })
    .then(res => {
        // Check if the response was OK (status 200-299)
        if (!res.ok) {
            // If not OK, parse the error message from the response
            return res.json().then(errorData => {
                const errorMessage = errorData.reply || `HTTP error! status: ${res.status}`;
                throw new Error(errorMessage);
            });
        }
        return res.json();
    })
    .then(data => {
        // Typing effect for bot reply
        const reply = data.reply;
        let i = 0;
        let spoken = false;
        botMsg.innerHTML = `<div class="bubble bot" tabindex="-1"></div>`;
        const bubble = botMsg.querySelector('.bubble.bot');
        function typeChar() {
            if (i < reply.length) {
                bubble.innerHTML += reply[i] === '\n' ? '<br>' : reply[i];
                i++;
                setTimeout(typeChar, 18 + Math.random() * 30);
                chatArea.scrollTop = chatArea.scrollHeight;
            } else {
                chatArea.scrollTop = chatArea.scrollHeight;
                // Speak the reply after typing is done (or you can speak as it types)
                if (!spoken) {
                    speakText(reply.replace(/<br>/g, '\n'));
                    spoken = true;
                }
            }
        }
        typeChar();
    })
    .catch(error => {
        console.error("Fetch error:", error); // Log the actual error
        let displayError = "Sorry, I couldn't process your request right now.";
        // If the error message from the server is meaningful, use it.
        if (error.message && error.message.includes("HTTP error!")) {
             displayError = `Server error: ${error.message}`;
        } else if (error.message) {
            displayError = error.message; // Use the specific message from throw new Error
        }
        botMsg.innerHTML = `<div class="bubble bot" tabindex="-1">${displayError}</div>`;
        chatArea.scrollTop = chatArea.scrollHeight;
    });

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

let recognizing = false;
let recognition;

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true; // Enable interim results
    recognition.lang = 'en-US';

    recognition.onstart = function() {
        recognizing = true;
        searchMic.style.color = '#1ec31e'; // Green
    };

    recognition.onend = function() {
        recognizing = false;
        searchMic.style.color = ''; // Reset to default
    };

    recognition.onresult = function(event) {
        let interim_transcript = '';
        let final_transcript = '';
        for (let i = 0; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                final_transcript += event.results[i][0].transcript;
            } else {
                interim_transcript += event.results[i][0].transcript;
            }
        }
        // Show both final and interim in the input
        searchInput.value = (final_transcript + interim_transcript).trim();
        searchInput.dispatchEvent(new Event('input')); // Update icon if needed
    };
}

searchMicSpan.addEventListener('click', function() {
    if (searchMic.classList.contains('fa-paper-plane')) {
        sendMessage();
    } else if (recognition) {
        if (!recognizing) {
            recognition.start();
        } else {
            recognition.stop();
        }
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

let voiceEnabled = true;
const voiceToggle = document.getElementById('voice-toggle');

// Toggle voice on/off
voiceToggle.addEventListener('click', function() {
    voiceEnabled = !voiceEnabled;
    voiceToggle.querySelector('i').className = voiceEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
});

// Helper to speak text
function speakText(text) {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel(); // Stop any previous speech
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-US';
    utter.rate = 1.02;
    window.speechSynthesis.speak(utter);
}