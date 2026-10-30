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
            
            // Allow safe action button pills generated by the backend assistant
            formattedLine = formattedLine
                .replace(/&lt;button class=&#39;action-pill-btn&#39; onclick=&#39;(.*?)&#39;&gt;(.*?)&lt;\/button&gt;/g, "<button class='action-pill-btn' onclick='$1'>$2</button>")
                .replace(/&lt;button class=\"action-pill-btn\" onclick=\"(.*?)\"&gt;(.*?)&lt;\/button&gt;/g, "<button class='action-pill-btn' onclick='$1'>$2</button>");
            
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
const scrollBottomBtn = document.getElementById("scroll-bottom-btn");
const inputAudioWave = document.getElementById("input-audio-wave");

// Progressive Web App (PWA) Registration
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/service-worker.js").catch(() => {});
    });
}

function scrollToBottom() {
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
    if (scrollBottomBtn) {
        scrollBottomBtn.classList.remove("visible");
    }
}

// Scroll to bottom trigger & listener
if (chatBox && scrollBottomBtn) {
    chatBox.addEventListener("scroll", () => {
        const distFromBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight;
        if (distFromBottom > 130) {
            scrollBottomBtn.classList.add("visible");
        } else {
            scrollBottomBtn.classList.remove("visible");
        }
    });

    scrollBottomBtn.addEventListener("click", () => {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });
    });
}

// Dynamic Time-Based Greeting
function updateGreeting() {
    const hour = new Date().getHours();
    let greet = "Namaste! 🙏 Welcome to GH Raisoni College Assistant.";
    if (hour >= 5 && hour < 12) greet = "Good Morning! ☀️ Welcome to GH Raisoni College Assistant.";
    else if (hour >= 12 && hour < 17) greet = "Good Afternoon! 🌤️ Welcome to GH Raisoni College Assistant.";
    else if (hour >= 17 && hour < 22) greet = "Good Evening! 🌆 Welcome to GH Raisoni College Assistant.";
    else greet = "Hello Night Owl! 🌙 Welcome to GH Raisoni College Assistant.";

    const greetElem = document.getElementById("welcome-greeting-text");
    if (greetElem) greetElem.textContent = greet;
}
updateGreeting();

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
    const btn = document.getElementById("theme-toggle-btn");
    if (btn) {
        const icon = btn.querySelector(".theme-icon") || btn;
        icon.textContent = theme === "dark" ? "☀️" : "🌙";
    }
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    setTheme(current === "dark" ? "light" : "dark");
}
window.toggleTheme = toggleTheme;

if (themeToggleBtn) {
    themeToggleBtn.onclick = toggleTheme;
}

function initSound() {
    if (soundToggleBtn) {
        const updateSoundLabel = () => {
            const icon = soundToggleBtn.querySelector(".sound-icon");
            const labelSpan = soundToggleBtn.querySelector("span:not(.sound-icon)");
            if (icon) icon.textContent = soundFX.enabled ? "🔔" : "🔕";
            if (labelSpan) labelSpan.textContent = soundFX.enabled ? "Chat Sounds: On" : "Chat Sounds: Muted";
        };
        updateSoundLabel();
        soundToggleBtn.addEventListener("click", () => {
            soundFX.enabled = !soundFX.enabled;
            localStorage.setItem("ghr_sound_fx", soundFX.enabled);
            updateSoundLabel();
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
        if (inputAudioWave) inputAudioWave.classList.add("active");
        if (speechStatus) speechStatus.textContent = "Listening... Speak now";
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        if (speechStatus) speechStatus.textContent = "";
        stopRecording();
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
    if (inputAudioWave) inputAudioWave.classList.remove("active");
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
        if (inputAudioWave) inputAudioWave.classList.remove("active");
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
    if (inputAudioWave) inputAudioWave.classList.add("active");

    utterance.onend = () => {
        if (btnElement) {
            btnElement.textContent = "🔊 Listen";
            btnElement.classList.remove("active");
        }
        if (inputAudioWave) inputAudioWave.classList.remove("active");
        activeUtterance = null;
    };

    utterance.onerror = () => {
        if (btnElement) {
            btnElement.textContent = "🔊 Listen";
            btnElement.classList.remove("active");
        }
        if (inputAudioWave) inputAudioWave.classList.remove("active");
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

// Student profile trigger in header opens 3D Digital ID Pass
if (studentProfileTrigger) {
    studentProfileTrigger.addEventListener("click", () => {
        openIdCardModal();
    });
}

// ==========================================================================
// 11. Multilingual Support (English, मराठी, हिंदी)
// ==========================================================================

const I18N = {
    en: {
        brandTitle: "GH Raisoni College AI",
        brandSubtitle: "Skill Tech University · Pune (Wagholi & Yerawada)",
        statusText: "GHR Smart Assistant • 24/7 Academic, Admissions & Campus Support",
        topicsLabel: "Explore Popular Topics:",
        placeholder: "Ask about admissions, fees, timetable, can I bunk, canteen menu...",
        inputHint: "Press Enter ↵ to send • Type exit to end",
        welcomeTitle: "Namaste! 🙏 Welcome to GH Raisoni College Assistant.",
        welcomeDesc: "I'm here to answer questions regarding admissions, exams, fees, syllabus, hostel, placements, and campus facilities.",
        bunkBtn: "Bunk Calc",
        idPassBtn: "ID Pass",
        bonafideBtn: "Bonafide",
        sosBtn: "SOS",
    },
    mr: {
        brandTitle: "जीएच रायसोनी कॉलेज एआय",
        brandSubtitle: "स्किल टेक युनिव्हर्सिटी · पुणे (वाघोली आणि येरवडा)",
        statusText: "जीएचआर स्मार्ट असिस्टंट • २४/७ शैक्षणिक, प्रवेश आणि कॅम्पस सहाय्य",
        topicsLabel: "लोकप्रिय विषय शोधा:",
        placeholder: "प्रवेश, फी, परीक्षा वेळापत्रक, हजेरी, बंक, कँटीन मेनू विचारा...",
        inputHint: "पाठवण्यासाठी Enter ↵ दाबा • थांबवण्यासाठी exit टाइप करा",
        welcomeTitle: "नमस्कार! 🙏 जीएच रायसोनी कॉलेज असिस्टंटमध्ये आपले स्वागत आहे.",
        welcomeDesc: "प्रवेश, परीक्षा, फी, अभ्यासक्रम, वसतिगृह, प्लेसमेंट आणि कॅम्पस सुविधांबद्दल मी तुम्हाला मदत करण्यास तयार आहे.",
        bunkBtn: "बंक कॅल्क्युलेटर",
        idPassBtn: "आयडी पास",
        bonafideBtn: "बोनाफाइड",
        sosBtn: "तातडीची मदत (SOS)",
    },
    hi: {
        brandTitle: "जीएच रायसोनी कॉलेज एआई",
        brandSubtitle: "स्किल टेक यूनिवर्सिटी · पुणे (वाघोली एवं येरवडा)",
        statusText: "जीएचआर स्मार्ट सहायक • 24/7 शैक्षणिक, प्रवेश व परिसर सहायता",
        topicsLabel: "प्रमुख विषय देखें:",
        placeholder: "प्रवेश, फीस, परीक्षा, बंक कैलकुलेटर, कैंटीन मेन्यू पूछें...",
        inputHint: "भेजने के लिए Enter ↵ दबाएं • समाप्त करने के लिए exit टाइप करें",
        welcomeTitle: "नमस्ते! 🙏 जीएच रायसोनी कॉलेज सहायक में आपका स्वागत है।",
        welcomeDesc: "प्रवेश, परीक्षा, फीस, सिलेबस, हॉस्टल, प्लेसमेंट और कैंपस से जुड़े सभी सवालों के लिए मैं यहां हूं।",
        bunkBtn: "बंक कैलकुलेटर",
        idPassBtn: "आईडी पास",
        bonafideBtn: "बोनाफाइड",
        sosBtn: "आपातकालीन सहायता (SOS)",
    }
};

let currentLanguage = localStorage.getItem("ghr_lang") || "en";

function setLanguage(lang) {
    if (!I18N[lang]) return;
    currentLanguage = lang;
    localStorage.setItem("ghr_lang", lang);

    const data = I18N[lang];

    // Update Header & Brand
    const titleElem = document.getElementById("ui-brand-title");
    const subElem = document.getElementById("ui-brand-subtitle");
    const statusElem = document.getElementById("ui-status-text");
    const topicsElem = document.getElementById("ui-topics-label");
    const hintElem = document.getElementById("ui-input-hint");

    if (titleElem) titleElem.textContent = data.brandTitle;
    if (subElem) subElem.textContent = data.brandSubtitle;
    if (statusElem) statusElem.textContent = data.statusText;
    if (topicsElem) topicsElem.textContent = data.topicsLabel;
    if (userInput) userInput.placeholder = data.placeholder;
    if (hintElem) hintElem.innerHTML = data.inputHint;

    // Update active button state
    document.querySelectorAll(".lang-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.lang === lang);
    });

    showToast(lang === "mr" ? "मराठी भाषा निवडली आहे 🇮🇳" : lang === "hi" ? "हिंदी भाषा चुनी गई है 🇮🇳" : "English language set 🇬🇧");
}

document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        setLanguage(btn.dataset.lang);
    });
});

// Initialize saved language
if (currentLanguage !== "en") {
    setLanguage(currentLanguage);
}

// ==========================================================================
// 12. Modal Controllers & 3D Interactive Features
// ==========================================================================

function openModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.add("show");
    document.body.style.overflow = "hidden";
    soundFX.playReceive();
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.remove("show");
    document.body.style.overflow = "";
}

// Close modals when clicking outside modal-dialog
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("custom-modal-backdrop")) {
        e.target.classList.remove("show");
        document.body.style.overflow = "";
    }
});

// Escape key closes open modals
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        document.querySelectorAll(".custom-modal-backdrop.show").forEach((m) => {
            m.classList.remove("show");
        });
        document.body.style.overflow = "";
    }
});

// ID Card functions
function openIdCardModal() {
    const flipper = document.getElementById("id-card-flipper");
    if (flipper) {
        flipper.style.transform = "";
        flipper.classList.remove("flipped");
    }
    openModal("id-card-modal");
}

function flipIdCard(e) {
    if (e && e.stopPropagation) {
        e.stopPropagation();
    }
    const flipper = document.getElementById("id-card-flipper");
    if (flipper) {
        flipper.style.transform = "";
        flipper.classList.toggle("flipped");
        soundFX.playSend();
    }
}

const idCardFlipper = document.getElementById("id-card-flipper");
if (idCardFlipper) {
    idCardFlipper.onclick = flipIdCard;
}

// Bunk Calculator Functions
function openBunkModal() {
    openModal("bunk-modal");
    calculateBunk();
}

async function calculateBunk() {
    const totalInput = document.getElementById("bunk-total-input");
    const attendedInput = document.getElementById("bunk-attended-input");
    const targetInput = document.getElementById("bunk-target-input");

    const total = parseInt(totalInput ? totalInput.value : 60) || 60;
    const attended = parseInt(attendedInput ? attendedInput.value : 45) || 45;
    const target = parseFloat(targetInput ? targetInput.value : 75.0) || 75.0;

    const resCard = document.getElementById("bunk-result-card");
    const title = document.getElementById("bunk-res-title");
    const subtitle = document.getElementById("bunk-res-subtitle");
    const margin = document.getElementById("bunk-res-margin");
    const forecast = document.getElementById("bunk-res-forecast");
    const desc = document.getElementById("bunk-res-desc");
    const gaugeFill = document.getElementById("gauge-fill-circle");
    const gaugeVal = document.getElementById("gauge-val-text");
    const gaugeRuleChip = document.getElementById("gauge-rule-chip");

    if (!resCard) return;

    try {
        const response = await fetch("/api/calculate_bunk", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ total, attended, target })
        });
        const data = await response.json();

        const pct = Math.min(100, Math.max(0, parseFloat(data.current_percentage) || 0));
        if (gaugeVal) gaugeVal.textContent = `${pct.toFixed(1)}%`;
        if (gaugeFill) {
            const circumference = 251.32;
            const offset = circumference * (1 - (pct / 100));
            gaugeFill.style.strokeDashoffset = offset;
        }

        if (data.can_bunk) {
            resCard.className = "bunk-result-box safe";
            if (gaugeFill) gaugeFill.style.stroke = "#10b981";
            if (gaugeRuleChip) {
                gaugeRuleChip.className = "gauge-rule-pill safe";
                gaugeRuleChip.textContent = "✓ Safe Standing (≥ 75%)";
            }
            title.textContent = "Safe to Bunk! 🎉";
            subtitle.textContent = `Current Attendance: ${data.current_percentage}%`;
            margin.textContent = data.bunks_allowed;
            forecast.textContent = `${data.forecast_percentage}%`;
            desc.textContent = data.message;
        } else {
            resCard.className = "bunk-result-box shortage";
            if (gaugeFill) gaugeFill.style.stroke = pct >= 60 ? "#f59e0b" : "#ef4444";
            if (gaugeRuleChip) {
                gaugeRuleChip.className = pct >= 60 ? "gauge-rule-pill warning" : "gauge-rule-pill danger";
                gaugeRuleChip.textContent = pct >= 60 ? "⚠️ Detention Warning (60-75%)" : "🚨 Critical Shortage (<60%)";
            }
            title.textContent = "Detention Shortage Alert! 🚨";
            subtitle.textContent = `Current Attendance: ${data.current_percentage}%`;
            margin.textContent = `${data.lectures_needed} (Needed)`;
            forecast.textContent = `${data.forecast_percentage}%`;
            desc.textContent = data.message;
        }
    } catch (e) {
        // Fallback local computation
        const curr = ((attended / total) * 100).toFixed(1);
        subtitle.textContent = `Current Attendance: ${curr}%`;
        if (gaugeVal) gaugeVal.textContent = `${curr}%`;
        if (gaugeFill) {
            const pct = Math.min(100, Math.max(0, parseFloat(curr) || 0));
            const circumference = 251.32;
            gaugeFill.style.strokeDashoffset = circumference * (1 - (pct / 100));
            gaugeFill.style.stroke = pct >= 75 ? "#10b981" : (pct >= 60 ? "#f59e0b" : "#ef4444");
        }
    }
}

const runBunkCalcBtn = document.getElementById("run-bunk-calc-btn");
if (runBunkCalcBtn) {
    runBunkCalcBtn.addEventListener("click", calculateBunk);
}

const pasteBunkToChatBtn = document.getElementById("paste-bunk-to-chat-btn");
if (pasteBunkToChatBtn) {
    pasteBunkToChatBtn.addEventListener("click", () => {
        closeModal("bunk-modal");
        sendMessage("can I bunk?");
    });
}

// Bonafide Certificate Functions
function openBonafideModal() {
    const today = new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
    const dateElem = document.getElementById("cert-today-date");
    if (dateElem) dateElem.textContent = today;
    openModal("bonafide-modal");
}

function updateBonafidePurpose() {
    const picker = document.getElementById("bonafide-purpose");
    const disp = document.getElementById("cert-purpose-display");
    if (picker && disp) {
        disp.textContent = picker.value;
    }
}

function printBonafideCertificate() {
    window.print();
}

// Campus Floor Navigator Directory
const FLOOR_DATA = {
    ground: [
        { num: "Room 101", desc: "<strong>Central Admissions Office</strong> — Main Academic Foyer, counseling desks & prospectus" },
        { num: "Counter 4", desc: "<strong>Accounts & Fee Payments</strong> — ERP billing, DD submission & fee receipts" },
        { num: "Room 102", desc: "<strong>Principal & Director Secretariat</strong> — Executive administrative suite" },
        { num: "Room 104", desc: "<strong>Scholarship & MahaDBT Helpdesk</strong> — State & national freeship portal" },
        { num: "Dispensary", desc: "<strong>Campus Medical Unit</strong> — Doctor on call, first aid (Sports Complex Wing)" }
    ],
    first: [
        { num: "Central Library", desc: "<strong>Knowledge Resource Centre</strong> — 25,000+ volumes, IEEE digital access" },
        { num: "Reading Hall", desc: "<strong>24/7 Quiet Study Area</strong> — Air-conditioned, open during exam weeks" },
        { num: "Staff Room A", desc: "<strong>BBA Computer Applications Faculty</strong> — Dr. A. Sharma & Prof. R. Verma" },
        { num: "Seminar Hall 1", desc: "<strong>Corporate Presentation Hall</strong> — 150-seat multimedia presentation hall" }
    ],
    second: [
        { num: "Lab 201-202", desc: "<strong>Advanced Computer Science Lab</strong> — Linux & Web Development environments" },
        { num: "Lab 203-204", desc: "<strong>AI & Data Analytics Lab</strong> — High-performance Python & GPU coding stations" },
        { num: "Placement Cell", desc: "<strong>Training & Placement Office (T&P)</strong> — Interview chambers & recruiter lounge" },
        { num: "Staff Room B", desc: "<strong>BCA & Information Technology Dept</strong> — Faculty workstations" }
    ],
    third: [
        { num: "Lab 301-304", desc: "<strong>Capstone Project & Research Labs</strong> — BBA-CA & BCA final year project hubs" },
        { num: "Audi 2", desc: "<strong>Central University Auditorium</strong> — 600-seat state-of-the-art stage & sound" },
        { num: "Robotics Hub", desc: "<strong>IoT & Embedded Systems Workshop</strong> — Hardware prototyping & 3D printing" }
    ]
};

let currentFloorKey = "ground";

function showFloor(key) {
    currentFloorKey = key;
    document.querySelectorAll(".floor-pill").forEach(p => p.classList.remove("active"));
    const container = document.getElementById("floor-list-container");
    if (!container || !FLOOR_DATA[key]) return;

    if (window.event && window.event.target && window.event.target.classList.contains("floor-pill")) {
        window.event.target.classList.add("active");
    }

    renderFloorList(FLOOR_DATA[key]);
    const searchInput = document.getElementById("floor-search-input");
    if (searchInput) searchInput.value = "";
}

function renderFloorList(rooms) {
    const container = document.getElementById("floor-list-container");
    if (!container) return;
    if (!rooms.length) {
        container.innerHTML = `<div class="room-item empty"><div class="room-desc">No matching rooms found on this floor.</div></div>`;
        return;
    }
    container.innerHTML = rooms.map(r => `
        <div class="room-item">
            <span class="room-num">${r.num}</span>
            <div class="room-desc">${r.desc}</div>
        </div>
    `).join("");
}

function filterFloorRooms() {
    const search = (document.getElementById("floor-search-input")?.value || "").toLowerCase().trim();
    if (!FLOOR_DATA[currentFloorKey]) return;
    if (!search) {
        renderFloorList(FLOOR_DATA[currentFloorKey]);
        return;
    }
    const filtered = FLOOR_DATA[currentFloorKey].filter(r => 
        r.num.toLowerCase().includes(search) || r.desc.toLowerCase().includes(search)
    );
    renderFloorList(filtered);
}

function openMapModal() {
    openModal("map-modal");
}

function openSosModal() {
    openModal("sos-modal");
}

// Navigation Tool Buttons
const navSosBtn = document.getElementById("nav-sos-btn");
if (navSosBtn) navSosBtn.addEventListener("click", () => openModal("sos-modal"));

// Header Tools Dropdown Controller
const headerToolsBtn = document.getElementById("header-tools-btn");
const headerDropdownMenu = document.getElementById("header-dropdown-menu");

if (headerToolsBtn && headerDropdownMenu) {
    headerToolsBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        headerDropdownMenu.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
        if (!headerDropdownMenu.contains(e.target) && e.target !== headerToolsBtn) {
            headerDropdownMenu.classList.remove("show");
        }
    });
}

// All Topics Collapsible Accordion Controller
function toggleAllTopics() {
    const tray = document.getElementById("all-topics-tray");
    const label = document.getElementById("toggle-topics-text");
    if (!tray || !label) return;

    const isCollapsed = tray.classList.toggle("collapsed");
    label.textContent = isCollapsed ? "Browse All 18 Topics ▾" : "Show Less ▴";
    soundFX.playReceive();
}

// Global Window Exports for Inline HTML onclick handlers
window.openModal = openModal;
window.closeModal = closeModal;
window.openBunkModal = openBunkModal;
window.openIdCardModal = openIdCardModal;
window.openBonafideModal = openBonafideModal;
window.openMapModal = openMapModal;
window.openSosModal = openSosModal;
window.showFloor = showFloor;
window.filterFloorRooms = filterFloorRooms;
window.flipIdCard = flipIdCard;
window.toggleAllTopics = toggleAllTopics;
window.toggleTheme = toggleTheme;
window.printBonafideCertificate = printBonafideCertificate;
window.updateBonafidePurpose = updateBonafidePurpose;
