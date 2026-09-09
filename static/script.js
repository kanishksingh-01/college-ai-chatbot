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
const endChatBtn = document.getElementById("end-chat-btn");

// Register service worker so the app becomes installable (PWA)
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/service-worker.js").catch(() => {});
    });
}

function formatTime(date = new Date()) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendUserMessage(text) {
    // Remove previous follow-up bars
    document.querySelectorAll(".follow-up-bar").forEach((bar) => bar.remove());

    const row = document.createElement("div");
    row.className = "msg-row user-row";
    row.innerHTML = `
        <div class="user-msg">
            <div class="user-text">${escapeHtml(text)}</div>
            <div class="msg-time user-time">${formatTime()}</div>
        </div>
        <div class="avatar user-avatar">🧑</div>
    `;
    chatBox.appendChild(row);
    scrollToBottom();
}

function appendBotMessage(text) {
    const row = document.createElement("div");
    row.className = "msg-row bot-row";
    row.innerHTML = `
        <div class="avatar bot-avatar">🤖</div>
        <div class="bot-msg">
            <div class="bot-text">${renderBotContent(text)}</div>
            <div class="bot-msg-footer">
                <span class="msg-time">${formatTime()}</span>
                <button class="copy-btn" title="Copy answer">📋 Copy</button>
            </div>
        </div>
    `;

    const copyBtn = row.querySelector(".copy-btn");
    copyBtn.addEventListener("click", () => {
        const contentToCopy = row.querySelector(".bot-text").innerText;
        navigator.clipboard.writeText(contentToCopy).then(() => {
            copyBtn.textContent = "✓ Copied";
            setTimeout(() => { copyBtn.textContent = "📋 Copy"; }, 1800);
        }).catch(() => {});
    });

    chatBox.appendChild(row);

    // Provide follow-up options ("Ask another question?" loop)
    appendFollowUpBar();

    scrollToBottom();
    if (!userInput.disabled) {
        userInput.focus();
    }
}

function appendFollowUpBar() {
    document.querySelectorAll(".follow-up-bar").forEach((b) => b.remove());

    const bar = document.createElement("div");
    bar.className = "follow-up-bar";
    bar.innerHTML = `
        <span class="follow-up-hint">Ask another question:</span>
        <button class="follow-up-chip" data-action="focus">💬 Type Query</button>
        <button class="follow-up-chip" data-query="Fee Structure">💰 Fees</button>
        <button class="follow-up-chip" data-query="Exam Timetable">📅 Timetable</button>
        <button class="follow-up-chip" data-query="Attendance Rules">📊 Attendance</button>
        <button class="follow-up-chip end-chip" data-action="end">⏹ End Chat</button>
    `;

    const focusBtn = bar.querySelector('[data-action="focus"]');
    if (focusBtn) {
        focusBtn.addEventListener("click", () => {
            userInput.focus();
            userInput.classList.add("input-highlight");
            setTimeout(() => userInput.classList.remove("input-highlight"), 1000);
        });
    }

    const endChip = bar.querySelector('[data-action="end"]');
    if (endChip) {
        endChip.addEventListener("click", endChatSession);
    }

    bar.querySelectorAll("[data-query]").forEach((btn) => {
        btn.addEventListener("click", () => sendMessage(btn.dataset.query));
    });

    chatBox.appendChild(bar);
}

function endChatSession() {
    document.querySelectorAll(".follow-up-bar").forEach((b) => b.remove());

    const endCard = document.createElement("div");
    endCard.className = "session-ended-card";
    endCard.innerHTML = `
        <div class="session-ended-icon">🏁</div>
        <div class="session-ended-title">Chat Session Ended</div>
        <div class="session-ended-desc">
            Thank you for using GH Raisoni College Assistant! You have successfully completed this chat session.
        </div>
        <button class="new-session-btn" id="restart-chat-btn">🔄 Start New Chat</button>
    `;

    chatBox.appendChild(endCard);
    scrollToBottom();

    userInput.disabled = true;
    sendBtn.disabled = true;
    userInput.placeholder = "Session ended. Click 'Start New Chat' to ask again.";

    endCard.querySelector("#restart-chat-btn").addEventListener("click", restartChatSession);
}

function restartChatSession() {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.placeholder = "Type your question...";
    userInput.value = "";

    chatBox.innerHTML = `
        <div class="msg-row bot-row">
            <div class="avatar bot-avatar">🤖</div>
            <div class="bot-msg">
                <div class="bot-text">
                    Hi! I'm your college assistant. Ask me anything below, or tap a topic to get started.
                </div>
                <div class="bot-msg-footer">
                    <span class="msg-time">${formatTime()}</span>
                </div>
            </div>
        </div>
    `;
    appendFollowUpBar();
    userInput.focus();
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

    // If user types exit / bye / quit, cleanly end session
    const lower = message.toLowerCase();
    if (["exit", "quit", "bye", "end"].includes(lower)) {
        appendUserMessage(message);
        userInput.value = "";
        setTimeout(endChatSession, 400);
        return;
    }

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

if (endChatBtn) {
    endChatBtn.addEventListener("click", endChatSession);
}

document.querySelectorAll(".quick-reply-btn").forEach((btn) => {
    btn.addEventListener("click", () => sendMessage(btn.dataset.query));
});
