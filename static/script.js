const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// Register service worker so the app becomes installable (PWA)
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/service-worker.js").catch(() => {});
    });
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "msg-row user-row";
    row.innerHTML = `
        <div class="user-msg"></div>
        <div class="avatar user-avatar">🧑</div>
    `;
    row.querySelector(".user-msg").textContent = text;
    chatBox.appendChild(row);
    scrollToBottom();
}

function appendBotMessage(text) {
    const row = document.createElement("div");
    row.className = "msg-row bot-row";
    row.innerHTML = `
        <div class="avatar bot-avatar">🤖</div>
        <div class="bot-msg"></div>
    `;
    row.querySelector(".bot-msg").textContent = text;
    chatBox.appendChild(row);
    scrollToBottom();
}

function showTypingIndicator() {
    const row = document.createElement("div");
    row.className = "msg-row bot-row";
    row.id = "typing-row";
    row.innerHTML = `
        <div class="avatar bot-avatar">🤖</div>
        <div class="bot-msg">
            <div class="typing-dots"><span></span><span></span><span></span></div>
        </div>
    `;
    chatBox.appendChild(row);
    scrollToBottom();
}

function removeTypingIndicator() {
    const row = document.getElementById("typing-row");
    if (row) row.remove();
}

async function sendMessage(overrideText) {
    const message = (overrideText !== undefined ? overrideText : userInput.value).trim();
    if (!message) return;

    appendUserMessage(message);
    userInput.value = "";

    showTypingIndicator();

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        const data = await res.json();

        // small delay so the typing indicator feels natural, not instant
        setTimeout(() => {
            removeTypingIndicator();
            appendBotMessage(data.response);
        }, 450);
    } catch (err) {
        removeTypingIndicator();
        appendBotMessage("Something went wrong. Please try again.");
    }
}

sendBtn.addEventListener("click", () => sendMessage());
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

document.querySelectorAll(".quick-reply-btn").forEach((btn) => {
    btn.addEventListener("click", () => sendMessage(btn.dataset.query));
});
