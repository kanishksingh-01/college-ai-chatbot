function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// Converts a chunk of "| a | b |" pipe-table lines into a real <table>.
// Any text outside table blocks is escaped and line-broken normally.
function renderBotContent(text) {
    const lines = text.split("\n");
    let html = "";
    let i = 0;

    while (i < lines.length) {
        const line = lines[i];

        if (line.trim().startsWith("|")) {
            // collect the contiguous block of table lines
            const tableLines = [];
            while (i < lines.length && lines[i].trim().startsWith("|")) {
                tableLines.push(lines[i].trim());
                i++;
            }

            const rows = tableLines
                .map((l) => l.replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim()))
                .filter((cells) => !cells.every((c) => /^-+$/.test(c))); // drop separator row

            if (rows.length > 0) {
                html += '<table class="bot-table">';
                html += "<thead><tr>" + rows[0].map((c) => `<th>${escapeHtml(c)}</th>`).join("") + "</tr></thead>";
                if (rows.length > 1) {
                    html += "<tbody>";
                    for (let r = 1; r < rows.length; r++) {
                        html += "<tr>" + rows[r].map((c) => `<td>${escapeHtml(c)}</td>`).join("") + "</tr>";
                    }
                    html += "</tbody>";
                }
                html += "</table>";
            }
        } else {
            html += escapeHtml(line) + "<br>";
            i++;
        }
    }

    return html;
}

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
    row.querySelector(".bot-msg").innerHTML = renderBotContent(text);
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
