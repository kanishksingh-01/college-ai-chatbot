/**
 * GH Raisoni College Assistant - Advanced Client Application
 * Voice Input (Speech-to-Text), Speech Synthesis (Read Aloud), 
 * Light/Dark Mode, Web Audio FX, Markdown & Table Parsing, Feedback & Export
 */

// ==========================================================================
// 1. Utilities & Audio System
// ==========================================================================

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function formatTime(date = new Date()) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function showToast(message, duration = 2500) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), duration);
}

// Web Audio API Synthesizer for lightweight, dependency-free audio cues
class SoundFX {
    constructor() {
        this.ctx = null;
        this.enabled = localStorage.getItem("ghr_sound_fx") !== "false";
    }

    init() {
        if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioCtx();
        }
    }

    playSend() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        try {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(440, this.ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(700, this.ctx.currentTime + 0.08);
            gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start();
            osc.stop(this.ctx.currentTime + 0.08);
        } catch (e) {}
    }

    playReceive() {
        if (!this.enabled) return;
        this.init();
        if (!this.ctx) return;
        try {
            const now = this.ctx.currentTime;
            const osc1 = this.ctx.createOscillator();
            const gain1 = this.ctx.createGain();
            osc1.type = "sine";
            osc1.frequency.setValueAtTime(587.33, now); // D5
            gain1.gain.setValueAtTime(0.05, now);
            gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
            osc1.connect(gain1);
            gain1.connect(this.ctx.destination);
            osc1.start(now);
            osc1.stop(now + 0.12);

            const osc2 = this.ctx.createOscillator();
            const gain2 = this.ctx.createGain();
            osc2.type = "sine";
            osc2.frequency.setValueAtTime(880, now + 0.09); // A5
            gain2.gain.setValueAtTime(0.06, now + 0.09);
            gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
            osc2.connect(gain2);
            gain2.connect(this.ctx.destination);
            osc2.start(now + 0.09);
            osc2.stop(now + 0.22);
        } catch (e) {}
    }
}

const soundFX = new SoundFX();

// ==========================================================================
// 2. Markdown & Table Parser
// ==========================================================================

function renderBotContent(text) {
    const lines = text.split("\n");
    let html = "";
    let i = 0;

    while (i < lines.length) {
        const line = lines[i];

        // Detect pipe table blocks
        if (line.trim().startsWith("|")) {
            const tableLines = [];
            while (i < lines.length && lines[i].trim().startsWith("|")) {
                tableLines.push(lines[i].trim());
                i++;
            }

            const rows = tableLines
                .map((l) => l.replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim()))
                .filter((cells) => !cells.every((c) => /^-+$/.test(c))); // Drop markdown separator row

            if (rows.length > 0) {
                html += '<div class="bot-table-wrapper"><table class="bot-table">';
                html += "<thead><tr>" + rows[0].map((c) => `<th>${escapeHtml(c)}</th>`).join("") + "</tr></thead>";
                if (rows.length > 1) {
                    html += "<tbody>";
                    for (let r = 1; r < rows.length; r++) {
                        html += "<tr>" + rows[r].map((c) => `<td>${escapeHtml(c)}</td>`).join("") + "</tr>";
                    }
                    html += "</tbody>";
                }
                html += "</table></div>";
            }
        } else {
            // Process markdown formatting: bold **text**, bullet points •
            let formattedLine = escapeHtml(line);
            formattedLine = formattedLine.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
            html += formattedLine + "<br>";
            i++;
        }
    }

    return html;
}

// Clean text extractor for speech synthesis (skips tables)
function getSpeechText(rawText) {
    return rawText
        .split("\n")
        .filter(l => !l.trim().startsWith("|"))
        .join(" ")
        .replace(/\*\*/g, "")
        .replace(/•/g, "")
        .replace(/\s+/g, " ")
        .trim();
}

// ==========================================================================
// 3. Elements & State Initialization
// ==========================================================================

const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const endChatBtn = document.getElementById("end-chat-btn");
const micBtn = document.getElementById("mic-btn");
const speechStatus = document.getElementById("speech-status");
const themeToggleBtn = document.getElementById("theme-toggle-btn");
const soundToggleBtn = document.getElementById("sound-toggle-btn");
const exportChatBtn = document.getElementById("export-chat-btn");
const clearChatBtn = document.getElementById("clear-chat-btn");
const studentProfileTrigger = document.getElementById("student-profile-trigger");

// Progressive Web App (PWA) Registration
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/service-worker.js").catch(() => {});
    });
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ==========================================================================
// 4. Dark Mode & Sound Toggle Management
// ==========================================================================

function initTheme() {
    const savedTheme = localStorage.getItem("ghr_theme") || 
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    setTheme(savedTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("ghr_theme", theme);
    if (themeToggleBtn) {
        themeToggleBtn.querySelector(".theme-icon").textContent = theme === "dark" ? "☀️" : "🌙";
    }
}

if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "light";
        setTheme(current === "dark" ? "light" : "dark");
    });
}

function initSound() {
    if (soundToggleBtn) {
        soundToggleBtn.querySelector(".sound-icon").textContent = soundFX.enabled ? "🔔" : "🔕";
        soundToggleBtn.addEventListener("click", () => {
            soundFX.enabled = !soundFX.enabled;
            localStorage.setItem("ghr_sound_fx", soundFX.enabled);
            soundToggleBtn.querySelector(".sound-icon").textContent = soundFX.enabled ? "🔔" : "🔕";
            showToast(soundFX.enabled ? "Sound effects enabled 🔔" : "Sound effects muted 🔕");
        });
    }
}

initTheme();
initSound();

// Set welcome message timestamp
const welcomeTs = document.getElementById("welcome-timestamp");
if (welcomeTs) welcomeTs.textContent = formatTime();

// ==========================================================================
// 5. Speech-to-Text (Voice Input)
// ==========================================================================

let recognition = null;
let isRecording = false;

if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-IN";

    recognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add("active");
        userInput.parentElement.classList.add("listening");
        if (speechStatus) speechStatus.textContent = "Listening... Speak now";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        if (speechStatus) speechStatus.textContent = "";
        sendMessage(transcript);
    };

    recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        if (speechStatus) speechStatus.textContent = "";
        stopRecording();
        if (event.error === "not-allowed") {
            showToast("Microphone access was denied. Please allow mic permissions in your browser.");
        }
    };

    recognition.onend = () => {
        stopRecording();
    };
}

function stopRecording() {
    isRecording = false;
    if (micBtn) micBtn.classList.remove("active");
    if (userInput) userInput.parentElement.classList.remove("listening");
    if (speechStatus) speechStatus.textContent = "";
}

if (micBtn) {
    if (!recognition) {
        micBtn.style.opacity = "0.4";
        micBtn.title = "Speech recognition not supported in this browser (Use Chrome or Safari)";
        micBtn.addEventListener("click", () => {
            showToast("Voice input is supported in Google Chrome and Safari.");
        });
    } else {
        micBtn.addEventListener("click", () => {
            if (isRecording) {
                recognition.stop();
            } else {
                try {
                    recognition.start();
                } catch (e) {
                    recognition.stop();
                }
            }
        });
    }
}

// ==========================================================================
// 6. Speech Synthesis (Text-to-Speech Read Aloud)
// ==========================================================================

let activeUtterance = null;

function speakText(text, btnElement) {
    if (!("speechSynthesis" in window)) {
        showToast("Text-to-speech is not supported on this browser.");
        return;
    }

    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        document.querySelectorAll(".speak-btn").forEach(b => {
            b.textContent = "🔊 Listen";
            b.classList.remove("active");
        });
        if (btnElement && activeUtterance && activeUtterance.tagBtn === btnElement) {
            return;
        }
    }

    const clean = getSpeechText(text);
    if (!clean) return;

    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.lang = "en-IN";
    utterance.tagBtn = btnElement;
    activeUtterance = utterance;

    if (btnElement) {
        btnElement.textContent = "⏹ Stop";
        btnElement.classList.add("active");
    }

    utterance.onend = () => {
        if (btnElement) {
            btnElement.textContent = "🔊 Listen";
            btnElement.classList.remove("active");
        }
        activeUtterance = null;
    };

    utterance.onerror = () => {
        if (btnElement) {
            btnElement.textContent = "🔊 Listen";
            btnElement.classList.remove("active");
        }
        activeUtterance = null;
    };

    window.speechSynthesis.speak(utterance);
}

// ==========================================================================
// 7. Message Rendering & Actions
// ==========================================================================

function appendUserMessage(text) {
    document.querySelectorAll(".follow-up-bar").forEach((b) => b.remove());

    const row = document.createElement("div");
    row.className = "msg-row user-row";
    row.innerHTML = `
        <div class="user-msg">
            <div class="user-text">${escapeHtml(text)}</div>
            <div class="user-time">${formatTime()}</div>
        </div>
        <div class="avatar user-avatar">👤</div>
    `;
    chatBox.appendChild(row);
    scrollToBottom();
}

function appendBotMessage(text, category = null, historyId = null) {
    const row = document.createElement("div");
    row.className = "msg-row bot-row";
    
    const categoryTag = category ? `<span class="category-badge">${escapeHtml(category)}</span>` : "";

    row.innerHTML = `
        <div class="avatar bot-avatar">🤖</div>
        <div class="bot-msg">
            ${categoryTag}
            <div class="bot-text">${renderBotContent(text)}</div>
            <div class="bot-msg-footer">
                <span class="msg-time">${formatTime()}</span>
                <div class="msg-actions">
                    <button class="msg-action-btn copy-btn" title="Copy answer">📋 Copy</button>
                    <button class="msg-action-btn speak-btn" title="Listen to answer">🔊 Listen</button>
                    ${historyId ? `
                        <button class="msg-action-btn feedback-btn" data-rating="like" data-id="${historyId}" title="Helpful">👍</button>
                        <button class="msg-action-btn feedback-btn" data-rating="dislike" data-id="${historyId}" title="Needs Improvement">👎</button>
                    ` : ""}
                </div>
            </div>
        </div>
    `;

    // Copy Handler
    const copyBtn = row.querySelector(".copy-btn");
    copyBtn.addEventListener("click", () => {
        const textToCopy = row.querySelector(".bot-text").innerText;
        navigator.clipboard.writeText(textToCopy).then(() => {
            copyBtn.textContent = "✓ Copied";
            showToast("Copied answer to clipboard! 📋");
            setTimeout(() => { copyBtn.textContent = "📋 Copy"; }, 2000);
        }).catch(() => {});
    });

    // Speak Handler
    const speakBtn = row.querySelector(".speak-btn");
    speakBtn.addEventListener("click", () => {
        speakText(text, speakBtn);
    });

    // Feedback Handlers
    row.querySelectorAll(".feedback-btn").forEach((fBtn) => {
        fBtn.addEventListener("click", () => {
            const hId = fBtn.dataset.id;
            const rating = fBtn.dataset.rating;
            sendFeedback(hId, rating, row);
        });
    });

    chatBox.appendChild(row);
    appendFollowUpBar();
    scrollToBottom();

    if (!userInput.disabled) {
        userInput.focus();
    }
}

function sendFeedback(historyId, rating, rowElement) {
    fetch("/chat/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history_id: historyId, rating }),
    }).then(res => res.json()).then(data => {
        rowElement.querySelectorAll(".feedback-btn").forEach(b => b.remove());
        showToast(rating === "like" ? "Thank you for the positive feedback! 👍" : "Thank you for the feedback, we'll improve! 🙏");
    }).catch(() => {});
}

// Follow-Up Quick Suggestions Loop
function appendFollowUpBar() {
    document.querySelectorAll(".follow-up-bar").forEach((b) => b.remove());

    const bar = document.createElement("div");
    bar.className = "follow-up-bar";
    bar.innerHTML = `
        <span class="follow-up-hint">Suggested queries:</span>
        <button class="follow-up-chip" data-query="Admissions">🎓 Admissions</button>
        <button class="follow-up-chip" data-query="Fee Structure">💰 Fees</button>
        <button class="follow-up-chip" data-query="Exam Timetable">📅 Exams</button>
        <button class="follow-up-chip" data-query="Placements">💼 Placements</button>
        <button class="follow-up-chip" data-query="Hostel & Mess">🏢 Hostel</button>
        <button class="follow-up-chip end-chip" data-action="end">⏹ End Chat</button>
    `;

    const endChip = bar.querySelector('[data-action="end"]');
    if (endChip) {
        endChip.addEventListener("click", endChatSession);
    }

    bar.querySelectorAll("[data-query]").forEach((btn) => {
        btn.addEventListener("click", () => sendMessage(btn.dataset.query));
    });

    chatBox.appendChild(bar);
}

// ==========================================================================
// 8. Session Flow (End & Restart)
// ==========================================================================

function endChatSession() {
    document.querySelectorAll(".follow-up-bar").forEach((b) => b.remove());

    if (window.speechSynthesis) window.speechSynthesis.cancel();

    const endCard = document.createElement("div");
    endCard.className = "session-ended-card";
    endCard.innerHTML = `
        <div class="session-ended-icon">🎓</div>
        <div class="session-ended-title">Chat Session Completed</div>
        <div class="session-ended-desc">
            Thank you for consulting the GH Raisoni College Assistant! We hope your queries were resolved.
        </div>
        <button class="new-session-btn" id="restart-chat-btn">🔄 Start New Session</button>
    `;

    chatBox.appendChild(endCard);
    scrollToBottom();

    userInput.disabled = true;
    sendBtn.disabled = true;
    userInput.placeholder = "Session ended. Click 'Start New Session' to resume.";

    endCard.querySelector("#restart-chat-btn").addEventListener("click", restartChatSession);
}

function restartChatSession() {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.placeholder = "Ask about admissions, fees, timetable, hostal...";
    userInput.value = "";

    chatBox.innerHTML = `
        <div class="msg-row bot-row">
            <div class="avatar bot-avatar">🤖</div>
            <div class="bot-msg">
                <div class="bot-text">
                    <strong>Welcome back! 👋</strong><br>
                    How can I assist you with your college academics or campus inquiries today?
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

// Clear Chat Action
if (clearChatBtn) {
    clearChatBtn.addEventListener("click", () => {
        if (confirm("Clear all conversation messages?")) {
            restartChatSession();
            showToast("Conversation cleared 🗑️");
        }
    });
}

// Export Chat Action
if (exportChatBtn) {
    exportChatBtn.addEventListener("click", exportConversation);
}

function exportConversation() {
    const messages = chatBox.querySelectorAll(".msg-row");
    if (!messages.length) {
        showToast("No messages to export.");
        return;
    }

    let transcript = "GH Raisoni College AI Assistant - Chat Transcript\n";
    transcript += `Generated: ${new Date().toLocaleString()}\n`;
    transcript += "=".repeat(60) + "\n\n";

    messages.forEach((m) => {
        const isUser = m.classList.contains("user-row");
        const sender = isUser ? "STUDENT" : "BOT";
        const textElem = m.querySelector(isUser ? ".user-text" : ".bot-text");
        const timeElem = m.querySelector(isUser ? ".user-time" : ".msg-time");
        const text = textElem ? textElem.innerText.trim() : "";
        const time = timeElem ? timeElem.innerText.trim() : "";
        transcript += `[${time}] ${sender}:\n${text}\n\n`;
    });

    const blob = new Blob([transcript], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `college_chat_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast("Chat transcript downloaded! 📥");
}

// ==========================================================================
// 9. Typing Indicator & Message Dispatch
// ==========================================================================

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

    // Handle session end commands
    const lower = message.toLowerCase();
    if (["exit", "quit", "bye", "end", "stop"].includes(lower)) {
        appendUserMessage(message);
        userInput.value = "";
        setTimeout(endChatSession, 350);
        return;
    }

    appendUserMessage(message);
    userInput.value = "";
    soundFX.playSend();

    showTypingIndicator();

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        const data = await res.json();

        // Natural typing pause (350-500ms)
        setTimeout(() => {
            removeTypingIndicator();
            appendBotMessage(data.response, data.category, data.history_id);
            soundFX.playReceive();
        }, 420);
    } catch (err) {
        removeTypingIndicator();
        appendBotMessage("Connection error: Unable to reach the college assistant server. Please check your network.", null);
    }
}

// ==========================================================================
// 10. Event Listeners & Quick Prompts
// ==========================================================================

sendBtn.addEventListener("click", () => sendMessage());

userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

if (endChatBtn) {
    endChatBtn.addEventListener("click", endChatSession);
}

// Delegate category and prompt buttons
document.addEventListener("click", (e) => {
    const target = e.target.closest(".quick-reply-btn, .prompt-chip");
    if (target && target.dataset.query) {
        sendMessage(target.dataset.query);
    }
});

// Student profile trigger in header
if (studentProfileTrigger) {
    studentProfileTrigger.addEventListener("click", () => {
        sendMessage("my student profile summary");
    });
}
