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
function updateGreeting(lang) {
    const activeLang = lang || currentLanguage || "en";
    const hour = new Date().getHours();
    let greet = "Namaste! 🙏 Welcome to GH Raisoni College Assistant.";
    if (activeLang === "mr") {
        if (hour >= 5 && hour < 12) greet = "शुभ सकाळ! ☀️ जीएच रायसोनी कॉलेज असिस्टंटमध्ये आपले स्वागत आहे.";
        else if (hour >= 12 && hour < 17) greet = "शुभ दुपार! 🌤️ जीएच रायसोनी कॉलेज असिस्टंटमध्ये आपले स्वागत आहे.";
        else if (hour >= 17 && hour < 22) greet = "शुभ संध्याकाळ! 🌆 जीएच रायसोनी कॉलेज असिस्टंटमध्ये आपले स्वागत आहे.";
        else greet = "नमस्कार! 🌙 जीएच रायसोनी कॉलेज असिस्टंटमध्ये आपले स्वागत आहे.";
    } else if (activeLang === "hi") {
        if (hour >= 5 && hour < 12) greet = "सुप्रभात! ☀️ जीएच रायसोनी कॉलेज सहायक में आपका स्वागत है।";
        else if (hour >= 12 && hour < 17) greet = "शुभ दोपहर! 🌤️ जीएच रायसोनी कॉलेज सहायक में आपका स्वागत है।";
        else if (hour >= 17 && hour < 22) greet = "शुभ संध्या! 🌆 जीएच रायसोनी कॉलेज सहायक में आपका स्वागत है।";
        else greet = "नमस्ते! 🌙 जीएच रायसोनी कॉलेज सहायक में आपका स्वागत है।";
    } else {
        if (hour >= 5 && hour < 12) greet = "Good Morning! ☀️ Welcome to GH Raisoni College Assistant.";
        else if (hour >= 12 && hour < 17) greet = "Good Afternoon! 🌤️ Welcome to GH Raisoni College Assistant.";
        else if (hour >= 17 && hour < 22) greet = "Good Evening! 🌆 Welcome to GH Raisoni College Assistant.";
        else greet = "Hello Night Owl! 🌙 Welcome to GH Raisoni College Assistant.";
    }

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
    const isMr = currentLanguage === "mr";
    const isHi = currentLanguage === "hi";

    const hint = isMr ? "सुचवलेले प्रश्न:" : (isHi ? "सुझाए गए प्रश्न:" : "Suggested queries:");
    const adm = isMr ? "🎓 प्रवेश" : (isHi ? "🎓 प्रवेश" : "🎓 Admissions");
    const fee = isMr ? "💰 फी" : (isHi ? "💰 फीस" : "💰 Fees");
    const exam = isMr ? "📅 परीक्षा" : (isHi ? "📅 परीक्षा" : "📅 Exams");
    const place = isMr ? "💼 प्लेसमेंट" : (isHi ? "💼 प्लेसमेंट" : "💼 Placements");
    const hostel = isMr ? "🏢 वसतिगृह" : (isHi ? "🏢 छात्रावास" : "🏢 Hostel");
    const end = isMr ? "⏹ संवाद समाप्त" : (isHi ? "⏹ चैट समाप्त" : "⏹ End Chat");

    bar.innerHTML = `
        <span class="follow-up-hint">${hint}</span>
        <button class="follow-up-chip" data-query="Admission">${adm}</button>
        <button class="follow-up-chip" data-query="Fee Structure">${fee}</button>
        <button class="follow-up-chip" data-query="Exam Timetable">${exam}</button>
        <button class="follow-up-chip" data-query="Placements">${place}</button>
        <button class="follow-up-chip" data-query="Hostel & Mess">${hostel}</button>
        <button class="follow-up-chip end-chip" data-action="end">${end}</button>
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

    const isMr = currentLanguage === "mr";
    const isHi = currentLanguage === "hi";

    const title = isMr ? "संवाद सत्र समाप्त झाला" : (isHi ? "चैट सत्र समाप्त" : "Chat Session Completed");
    const desc = isMr 
        ? "जीएच रायसोनी कॉलेज असिस्टंट वापरल्याबद्दल धन्यवाद! आशा आहे की तुमच्या सर्व प्रश्नांचे निरसन झाले असेल."
        : (isHi 
            ? "जीएच रायसोनी कॉलेज सहायक का उपयोग करने के लिए धन्यवाद! आशा है कि आपके प्रश्नों का समाधान हुआ होगा।"
            : "Thank you for consulting the GH Raisoni College Assistant! We hope your queries were resolved.");
    const restartBtnText = isMr ? "🔄 नवीन संवाद सुरू करा" : (isHi ? "🔄 नया सत्र शुरू करें" : "🔄 Start New Session");

    const endCard = document.createElement("div");
    endCard.className = "session-ended-card";
    endCard.innerHTML = `
        <div class="session-ended-icon">🎓</div>
        <div class="session-ended-title">${title}</div>
        <div class="session-ended-desc">${desc}</div>
        <button class="new-session-btn" id="restart-chat-btn">${restartBtnText}</button>
    `;

    chatBox.appendChild(endCard);
    scrollToBottom();

    userInput.disabled = true;
    sendBtn.disabled = true;
    userInput.placeholder = isMr ? "संवाद समाप्त झाला. पुन्हा सुरू करण्यासाठी बटण दाबा." : (isHi ? "सत्र समाप्त हुआ। फिर से शुरू करने के लिए बटन दबाएं।" : "Session ended. Click 'Start New Session' to resume.");

    endCard.querySelector("#restart-chat-btn").addEventListener("click", restartChatSession);
}

function restartChatSession() {
    userInput.disabled = false;
    sendBtn.disabled = false;
    const isMr = currentLanguage === "mr";
    const isHi = currentLanguage === "hi";

    userInput.placeholder = isMr ? "प्रवेश, फी, परीक्षा, हजेरी, बंक विचारा..." : (isHi ? "प्रवेश, फीस, परीक्षा, बंक पूछें..." : "Ask about admissions, fees, timetable, can I bunk...");
    userInput.value = "";

    const welcomeBack = isMr ? "पुन्हा स्वागत आहे! 👋" : (isHi ? "वापसी पर स्वागत है! 👋" : "Welcome back! 👋");
    const subText = isMr 
        ? "आज मी तुम्हाला कॉलेज अभ्यासक्रम किंवा कॅम्पसबद्दल कशी मदत करू शकतो?" 
        : (isHi 
            ? "आज मैं कॉलेज या परिसर से जुड़ी आपकी किस प्रकार सहायता कर सकता हूँ?" 
            : "How can I assist you with your college academics or campus inquiries today?");

    chatBox.innerHTML = `
        <div class="msg-row bot-row">
            <div class="avatar bot-avatar">🤖</div>
            <div class="bot-msg">
                <div class="bot-text">
                    <strong>${welcomeBack}</strong><br>
                    ${subText}
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
    if (["exit", "quit", "bye", "end", "stop", "थांबवा", "बाहेर", "अलविदा", "बंद"].includes(lower)) {
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
            body: JSON.stringify({ message, lang: currentLanguage }),
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
        const errText = currentLanguage === "mr"
            ? "सर्व्हरशी संपर्क साधता आला नाही. कृपया नेटवर्क कनेक्शन तपासा."
            : (currentLanguage === "hi"
                ? "सर्वर से संपर्क करने में असमर्थ। कृपया नेटवर्क कनेक्शन जांचें।"
                : "Connection error: Unable to reach the college assistant server. Please check your network.");
        appendBotMessage(errText, null);
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

const TOPIC_I18N = {
    "Admission": { en: "Admission", mr: "प्रवेश प्रक्रिया", hi: "प्रवेश प्रक्रिया" },
    "Fee Structure": { en: "Fee Structure", mr: "फी रचना", hi: "फीस संरचना" },
    "Exam Timetable": { en: "Exam Timetable", mr: "परीक्षा वेळापत्रक", hi: "परीक्षा समय सारणी" },
    "Attendance Rules": { en: "Attendance Rules", mr: "हजेरी नियम (७५%)", hi: "उपस्थिति नियम (75%)" },
    "Placements": { en: "Placements", mr: "प्लेसमेंट व करिअर", hi: "प्लेसमेंट व करियर" },
    "Canteen & Mess Menu": { en: "Canteen & Mess", mr: "कॅन्टीन व मेस", hi: "कैंटीन व मेस" },
    "Library Timings": { en: "Library Timings", mr: "ग्रंथालय वेळ", hi: "पुस्तकालय समय" },
    "Course Information": { en: "Course Information", mr: "अभ्यासक्रम माहिती", hi: "पाठ्यक्रम विवरण" },
    "Faculty Contact": { en: "Faculty Contact", mr: "प्राध्यापक संपर्क", hi: "शिक्षक संपर्क" },
    "Branch Change": { en: "Branch Change", mr: "शाखा बदल", hi: "शाखा परिवर्तन" },
    "Hostel & Mess": { en: "Hostel & Mess", mr: "वसतिगृह व मेस", hi: "छात्रावास व मेस" },
    "Scholarships": { en: "Scholarships", mr: "शिष्यवृत्ती", hi: "छात्रवृत्ति" },
    "Clubs & Extracurriculars": { en: "Clubs & Events", mr: "क्लब्स व उपक्रम", hi: "क्लब व गतिविधियां" },
    "Emergency & Helpline": { en: "Emergency & Helpline", mr: "आपत्कालीन मदत", hi: "आपातकालीन हेल्पलाइन" },
    "Campus Location & Map": { en: "Campus Location", mr: "कॅम्पस स्थान व पत्ता", hi: "परिसर स्थान व पता" },
    "Campus Floor & Room Locator": { en: "Floor Navigator", mr: "मजला व कक्ष शोधक", hi: "मंजिल एवं कक्ष खोजक" },
    "Bonafide & Document Services": { en: "Bonafide Certificate", mr: "बोनाफाइड प्रमाणपत्र", hi: "बोनाफाइड प्रमाण पत्र" },
    "Attendance & Bunk Calculator Guide": { en: "Bunk Calculator Guide", mr: "बंक कॅल्क्युलेटर नियम", hi: "बंक कैलकुलेटर नियम" },
    "Campus Amenities & WiFi": { en: "Amenities & WiFi", mr: "वायफाय व सुविधा", hi: "वाई-फाई व सुविधाएं" },
    "Academic Regulations & Grading": { en: "Grading & Regulations", mr: "शैक्षणिक नियम व ग्रेडिंग", hi: "अकादमिक नियम व ग्रेडिंग" },
    "University Leadership & Faculty": { en: "University Leadership", mr: "विद्यापीठ नेतृत्व", hi: "विश्वविद्यालय नेतृत्व" },
    "Academic Calendar & Holidays": { en: "Academic Calendar", mr: "दिनदर्शिका व सुट्ट्या", hi: "कैलेंडर व छुट्टियां" },
    "Student Life & Chatbot Info": { en: "Student Life", mr: "विद्यार्थी जीवन", hi: "विद्यार्थी जीवन" }
};

const I18N = {
    en: {
        brandTitle: "GH Raisoni College AI",
        brandSubtitle: "Skill Tech University · Pune (Wagholi & Yerawada)",
        brandBadge: "AUTONOMOUS 2026–27",
        aiOnline: "AI Online",
        sos: '<span class="sos-pulse-dot"></span> 🚨 SOS',
        logout: "Logout",
        login: "Student Login",
        admin: "Admin",
        statusText: "GHR Smart Assistant • 24/7 Academic, Admissions & Campus Support",
        stripBunk: "🎯 Bunk Calc",
        stripId: "🪪 ID Pass",
        stripBonafide: "📄 Bonafide",
        stripMap: "🗺️ Floor Map",
        endChat: "⏹ End Chat",
        welcomeSub: "I am your 24/7 campus companion. Ask questions about admissions, fees, timetable, detention rules, or explore our interactive tools below.",
        tileBunkTitle: "Bunk Calculator",
        tileBunkSub: "75% Rule & Safe Margins",
        tileIdTitle: "3D Digital ID Pass",
        tileIdSub: "QR Verified Student Pass",
        tileBonafideTitle: "Bonafide / NOC",
        tileBonafideSub: "Instant Download & Print",
        tileMapTitle: "Floor Navigator",
        tileMapSub: "Labs, Rooms & Counters",
        studentNotice: "✨ Logged in as <strong>{name}</strong>. Quick questions:",
        chipBunk: "🎯 Can I Bunk?",
        chipAtt: "📊 My Attendance",
        chipId: "🪪 Digital ID Card",
        chipBonafide: "📄 Bonafide Letter",
        chipFee: "💰 My Fee Balance",
        chipCgpa: "🌟 My CGPA",
        topicsLabel: "Explore Campus Topics:",
        toggleTopicsCollapsed: "Browse All Topics ▾",
        toggleTopicsExpanded: "Show Less ▴",
        placeholder: "Ask about admissions, fees, timetable, can I bunk, canteen menu...",
        inputHint: "Press <strong>Enter ↵</strong> to send • Type <code>exit</code> to end",
        toast: "English language set 🇬🇧",
        copyBtn: "📋 Copy",
        listenBtn: "🔊 Listen"
    },
    mr: {
        brandTitle: "जीएच रायसोनी कॉलेज एआय",
        brandSubtitle: "स्किल टेक युनिव्हर्सिटी · पुणे (वाघोली आणि येरवडा)",
        brandBadge: "स्वायत्त २०२६–२७",
        aiOnline: "एआय सक्रिय",
        sos: '<span class="sos-pulse-dot"></span> 🚨 आपत्कालीन मदत',
        logout: "लॉगआउट",
        login: "विद्यार्थी लॉगिन",
        admin: "प्रशासक",
        statusText: "जीएचआर स्मार्ट असिस्टंट • २४/७ शैक्षणिक, प्रवेश आणि कॅम्पस सहाय्य",
        stripBunk: "🎯 बंक कॅल्क",
        stripId: "🪪 डिजिटल आयडी",
        stripBonafide: "📄 बोनाफाइड",
        stripMap: "🗺️ फ्लोअर नकाशा",
        endChat: "⏹ संवाद समाप्त",
        welcomeSub: "मी तुमचा २४/७ कॅम्पस सहाय्यक आहे. प्रवेश, फी, वेळापत्रक, हजेरी नियम विचारा किंवा खालील साधने वापरा.",
        tileBunkTitle: "बंक कॅल्क्युलेटर",
        tileBunkSub: "७५% हजेरी नियम व सुरक्षित बंक",
        tileIdTitle: "३D डिजिटल आयडी पास",
        tileIdSub: "क्युआर कोड प्रमाणित विद्यार्थी पास",
        tileBonafideTitle: "बोनाफाइड / एनओसी",
        tileBonafideSub: "त्वरित डाउनलोड आणि प्रिंट करा",
        tileMapTitle: "कॅम्पस फ्लोअर शोधक",
        tileMapSub: "लॅब्स, वर्गखोल्या व काउन्टर्स",
        studentNotice: "✨ <strong>{name}</strong> म्हणून लॉगिन केले आहे. द्रुत प्रश्न:",
        chipBunk: "🎯 मी आज बंक करू शकतो का?",
        chipAtt: "📊 माझी हजेरी",
        chipId: "🪪 डिजिटल आयडी कार्ड",
        chipBonafide: "📄 बोनाफाइड प्रमाणपत्र",
        chipFee: "💰 माझी उर्वरित फी",
        chipCgpa: "🌟 माझे सीजीपीए (CGPA)",
        topicsLabel: "लोकप्रिय विषय शोधा:",
        toggleTopicsCollapsed: "सर्व विषय पहा ▾",
        toggleTopicsExpanded: "कमी दाखवा ▴",
        placeholder: "प्रवेश, फी, परीक्षा वेळापत्रक, हजेरी, बंक, कॅन्टीन मेनू विचारा...",
        inputHint: "पाठवण्यासाठी <strong>Enter ↵</strong> दाबा • थांबवण्यासाठी <code>exit</code> टाइप करा",
        toast: "मराठी भाषा निवडली आहे 🇮🇳",
        copyBtn: "📋 कॉपी",
        listenBtn: "🔊 ऐका"
    },
    hi: {
        brandTitle: "जीएच रायसोनी कॉलेज एआई",
        brandSubtitle: "स्किल टेक यूनिवर्सिटी · पुणे (वाघोली एवं येरवडा)",
        brandBadge: "स्वायत्त 2026–27",
        aiOnline: "एआई ऑनलाइन",
        sos: '<span class="sos-pulse-dot"></span> 🚨 आपातकालीन सहायता',
        logout: "लॉगआउट",
        login: "छात्र लॉगिन",
        admin: "एडमिन",
        statusText: "जीएचआर स्मार्ट सहायक • 24/7 शैक्षणिक, प्रवेश व परिसर सहायता",
        stripBunk: "🎯 बंक कैल्क",
        stripId: "🪪 डिजिटल आईडी",
        stripBonafide: "📄 बोनाफाइड",
        stripMap: "🗺️ फ्लोर नक्शा",
        endChat: "⏹ चैट समाप्त",
        welcomeSub: "मैं आपका 24/7 कैंपस साथी हूँ। प्रवेश, फीस, समय सारणी, उपस्थिति नियम पूछें या नीचे दिए गए टूल्स का उपयोग करें।",
        tileBunkTitle: "बंक कैलकुलेटर",
        tileBunkSub: "75% उपस्थिति व सुरक्षित बंक",
        tileIdTitle: "3D डिजिटल आईडी कार्ड",
        tileIdSub: "क्यूआर कोड सत्यापित छात्र पास",
        tileBonafideTitle: "बोनाफाइड / एनओसी",
        tileBonafideSub: "तुरंत डाउनलोड और प्रिंट करें",
        tileMapTitle: "परिसर फ्लोर नेविगेटर",
        tileMapSub: "लैब्स, कक्षाएं और काउंटर्स",
        studentNotice: "✨ <strong>{name}</strong> के रूप में लॉगिन किया गया। त्वरित प्रश्न:",
        chipBunk: "🎯 क्या मैं बंक कर सकता हूँ?",
        chipAtt: "📊 मेरी उपस्थिति",
        chipId: "🪪 डिजिटल आईडी कार्ड",
        chipBonafide: "📄 बोनाफाइड प्रमाण पत्र",
        chipFee: "💰 मेरी बकाया फीस",
        chipCgpa: "🌟 मेरा सीजीपीए (CGPA)",
        topicsLabel: "प्रमुख विषय देखें:",
        toggleTopicsCollapsed: "सभी विषय देखें ▾",
        toggleTopicsExpanded: "कम दिखाएं ▴",
        placeholder: "प्रवेश, फीस, परीक्षा, बंक कैलकुलेटर, कैंटीन मेन्यू पूछें...",
        inputHint: "भेजने के लिए <strong>Enter ↵</strong> दबाएं • समाप्त करने के लिए <code>exit</code> टाइप करें",
        toast: "हिंदी भाषा चुनी गई है 🇮🇳",
        copyBtn: "📋 कॉपी",
        listenBtn: "🔊 सुनें"
    }
};

let currentLanguage = localStorage.getItem("ghr_lang") || "en";

function setLanguage(lang) {
    if (!I18N[lang]) return;
    currentLanguage = lang;
    localStorage.setItem("ghr_lang", lang);

    const data = I18N[lang];

    // 1. Header & Brand
    const titleElem = document.getElementById("ui-brand-title");
    const subElem = document.getElementById("ui-brand-subtitle");
    if (titleElem) titleElem.textContent = data.brandTitle;
    if (subElem) subElem.textContent = data.brandSubtitle;

    const brandBadge = document.getElementById("brand-badge-text");
    if (brandBadge) brandBadge.textContent = data.brandBadge;

    const aiLabel = document.getElementById("ai-status-label");
    if (aiLabel) aiLabel.textContent = data.aiOnline;

    const navSos = document.getElementById("nav-sos-btn");
    if (navSos) navSos.innerHTML = data.sos;

    const navLogout = document.getElementById("ui-nav-logout");
    if (navLogout) navLogout.textContent = data.logout;

    const navLogin = document.getElementById("ui-nav-login");
    if (navLogin) navLogin.textContent = data.login;

    const navAdmin = document.getElementById("nav-admin-btn");
    if (navAdmin) navAdmin.textContent = data.admin;

    // 2. Chat Status Strip
    const statusElem = document.getElementById("ui-status-text");
    if (statusElem) statusElem.textContent = data.statusText;

    const stripBunk = document.getElementById("strip-btn-bunk");
    if (stripBunk) stripBunk.textContent = data.stripBunk;

    const stripId = document.getElementById("strip-btn-id");
    if (stripId) stripId.textContent = data.stripId;

    const stripBonafide = document.getElementById("strip-btn-bonafide");
    if (stripBonafide) stripBonafide.textContent = data.stripBonafide;

    const stripMap = document.getElementById("strip-btn-map");
    if (stripMap) stripMap.textContent = data.stripMap;

    const endChat = document.getElementById("end-chat-btn");
    if (endChat) endChat.textContent = data.endChat;

    // 3. Welcome Message & Greeting
    updateGreeting(lang);

    const welcomeSub = document.getElementById("welcome-subtext");
    if (welcomeSub) welcomeSub.textContent = data.welcomeSub;

    // 4. 4 Interactive Service Tiles
    const tileBunkTitle = document.getElementById("tile-bunk-title");
    if (tileBunkTitle) tileBunkTitle.textContent = data.tileBunkTitle;
    const tileBunkSub = document.getElementById("tile-bunk-sub");
    if (tileBunkSub) tileBunkSub.textContent = data.tileBunkSub;

    const tileIdTitle = document.getElementById("tile-id-title");
    if (tileIdTitle) tileIdTitle.textContent = data.tileIdTitle;
    const tileIdSub = document.getElementById("tile-id-sub");
    if (tileIdSub) tileIdSub.textContent = data.tileIdSub;

    const tileBonafideTitle = document.getElementById("tile-bonafide-title");
    if (tileBonafideTitle) tileBonafideTitle.textContent = data.tileBonafideTitle;
    const tileBonafideSub = document.getElementById("tile-bonafide-sub");
    if (tileBonafideSub) tileBonafideSub.textContent = data.tileBonafideSub;

    const tileMapTitle = document.getElementById("tile-map-title");
    if (tileMapTitle) tileMapTitle.textContent = data.tileMapTitle;
    const tileMapSub = document.getElementById("tile-map-sub");
    if (tileMapSub) tileMapSub.textContent = data.tileMapSub;

    // 5. Student Logged In Notice Card
    const studentNotice = document.getElementById("student-notice-text");
    if (studentNotice) {
        const studentName = studentNotice.dataset.studentName || 
            (studentNotice.querySelector("strong") ? studentNotice.querySelector("strong").textContent : "Student");
        studentNotice.innerHTML = data.studentNotice.replace("{name}", studentName);
    }

    // 6. Student Quick Prompts Chips
    const chipBunk = document.getElementById("chip-bunk");
    if (chipBunk) chipBunk.textContent = data.chipBunk;
    const chipAtt = document.getElementById("chip-att");
    if (chipAtt) chipAtt.textContent = data.chipAtt;
    const chipId = document.getElementById("chip-id");
    if (chipId) chipId.textContent = data.chipId;
    const chipBonafide = document.getElementById("chip-bonafide");
    if (chipBonafide) chipBonafide.textContent = data.chipBonafide;
    const chipFee = document.getElementById("chip-fee");
    if (chipFee) chipFee.textContent = data.chipFee;
    const chipCgpa = document.getElementById("chip-cgpa");
    if (chipCgpa) chipCgpa.textContent = data.chipCgpa;

    // 7. Topics Header & Toggle Text
    const topicsElem = document.getElementById("ui-topics-label");
    if (topicsElem) topicsElem.textContent = data.topicsLabel;

    const toggleText = document.getElementById("toggle-topics-text");
    const tray = document.getElementById("all-topics-tray");
    if (toggleText) {
        const isCollapsed = !tray || tray.classList.contains("collapsed");
        toggleText.textContent = isCollapsed ? data.toggleTopicsCollapsed : data.toggleTopicsExpanded;
    }

    // 8. All Topic Chips
    document.querySelectorAll(".quick-reply-btn").forEach((btn) => {
        const q = btn.dataset.query;
        if (q && TOPIC_I18N[q] && TOPIC_I18N[q][lang]) {
            const span = btn.querySelector("span");
            if (span) span.textContent = TOPIC_I18N[q][lang];
        }
    });

    // 9. Input & Hint
    if (userInput) userInput.placeholder = data.placeholder;
    const hintElem = document.getElementById("ui-input-hint");
    if (hintElem) hintElem.innerHTML = data.inputHint;

    // 10. Update Active Button State
    document.querySelectorAll(".lang-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.lang === lang);
    });

    // 11. Welcome message copy/listen buttons
    const welcomeMsg = document.getElementById("welcome-message-content");
    if (welcomeMsg) {
        const parentMsg = welcomeMsg.closest(".bot-msg");
        if (parentMsg) {
            const copyBtn = parentMsg.querySelector(".copy-btn");
            if (copyBtn) copyBtn.textContent = data.copyBtn;
            const speakBtn = parentMsg.querySelector(".speak-btn");
            if (speakBtn && !speakBtn.classList.contains("active")) speakBtn.textContent = data.listenBtn;
        }
    }

    // 12. Voice Recognition Language
    if (recognition) {
        recognition.lang = lang === "mr" ? "mr-IN" : (lang === "hi" ? "hi-IN" : "en-IN");
    }

    showToast(data.toast);
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
    const data = I18N[currentLanguage] || I18N.en;
    label.textContent = isCollapsed ? data.toggleTopicsCollapsed : data.toggleTopicsExpanded;
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
