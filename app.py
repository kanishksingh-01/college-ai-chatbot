"""
app.py
Flask backend for the AI Chatbot for College project.
GH Raisoni College - BBA Computer Applications
"""

import os
import re
import csv
import io
import math
import sqlite3
import difflib
from flask import (
    Flask,
    request,
    jsonify,
    session,
    render_template,
    redirect,
    url_for,
    send_from_directory,
    Response,
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    import hashlib

    def generate_password_hash(password):
        salt = "7x4k8m9q2w1e6r3t"
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000).hex()
        return f"pbkdf2:sha256:600000${salt}${h}"

    def check_password_hash(p_hash, password):
        try:
            parts = p_hash.split("$")
            if len(parts) >= 3:
                salt = parts[-2]
                expected = parts[-1]
                h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000).hex()
                return h == expected
        except Exception:
            pass
        return False


app = Flask(__name__)
# In production (Render), set SECRET_KEY as an environment variable instead of hardcoding it.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-before-submission")
DB_NAME = "college_chatbot.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# Auto-check and update database seed on startup if required
try:
    from database import init_db
    _conn = get_db()
    _cnt = _conn.execute("SELECT COUNT(*) FROM college_info").fetchone()[0]
    _conn.close()
    if _cnt < 20:
        init_db()
except Exception as _e:
    pass


# ---------------- HYBRID AI: GOOGLE GEMINI FALLBACK ----------------

def ask_gemini(query):
    """
    Fallback to Google Gemini API when rule-based confidence is low.
    Grounded strictly as the official GH Raisoni College Assistant.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not gemini_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=gemini_key)
        system_instruction = (
            "You are the official AI Campus Assistant for GH Raisoni College (GH Raisoni International Skill Tech University, Pune - Wagholi & Yerawada campuses). "
            "You answer student and visitor questions concisely, politely, and accurately. "
            "Key facts: "
            "1. Locations: Wagholi Campus (Gat 1200 Domkhel Rd, Wagholi, Pune 412207) and Yerawada Campus (Nyati Unitree, Airport Rd, Pune 411006). "
            "2. Programs: BBA-CA, BCA, BCom (Comp Apps), MCA, Engineering. Affiliated to SPPU / autonomous Skill Tech University. "
            "3. Mandatory attendance: 75% minimum, with strict 4-tier detention policy. "
            "4. Accounts: Counter 4, Admin Block. Admissions: Room 101. Library: 1st floor, 8:30 AM - 7:00 PM. "
            "5. Emergency / Security: 24/7 Gate Control +91 20-67528000, Anti-Ragging: 1800-180-5522. "
            "Format responses cleanly with markdown bullet points and emojis where helpful. "
            "Do not hallucinate external policies. If unsure, advise visiting Admin Counter 4 or emailing admissions@ghrc.edu."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
                max_output_tokens=500,
            ),
        )
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
    return None


# ---------------- CHATBOT LOGIC (SYNONYM-AWARE FUZZY NLP & HYBRID CAMPUS REASONER) ----------------

SYNONYM_MAP = {
    "attend": ["attendance", "present", "lecture", "classes", "session"],
    "attending": ["attendance", "present", "lecture", "classes"],
    "miss": ["bunk", "absent", "skip", "attendance", "shortage"],
    "missing": ["bunk", "absent", "skip", "attendance"],
    "skip": ["bunk", "miss", "attendance"],
    "skipping": ["bunk", "miss", "attendance"],
    "bunk": ["miss class", "skip class", "attendance", "bunk calculator"],
    "absent": ["attendance", "leave", "medical leave", "detention"],
    "leave": ["medical leave", "absent", "attendance"],
    "food": ["canteen", "mess", "lunch", "breakfast", "menu"],
    "eat": ["canteen", "mess", "food"],
    "lunch": ["canteen", "mess", "food"],
    "breakfast": ["canteen", "mess", "food"],
    "tea": ["canteen", "snacks"],
    "coffee": ["canteen", "snacks"],
    "hostel": ["accommodation", "room", "stay", "warden"],
    "dorm": ["hostel", "room"],
    "stay": ["hostel", "accommodation"],
    "placement": ["job", "package", "recruiter", "salary", "companies", "tpo"],
    "job": ["placement", "package", "recruiter"],
    "package": ["placement", "salary", "recruiter"],
    "salary": ["placement", "package"],
    "companies": ["placement", "recruiter"],
    "company": ["placement", "recruiter"],
    "hiring": ["placement", "recruiter"],
    "exam": ["timetable", "schedule", "datesheet", "hall ticket", "admit card"],
    "exams": ["timetable", "schedule", "datesheet", "admit card"],
    "test": ["exam", "mid-term", "timetable"],
    "schedule": ["timetable", "exam", "datesheet"],
    "paper": ["exam", "timetable", "datesheet"],
    "cost": ["fee", "fees", "payment", "tuition"],
    "money": ["fee", "fees", "dues", "cost"],
    "dues": ["fee", "fees", "balance"],
    "paid": ["fee", "fees", "receipt"],
    "certificate": ["bonafide", "noc", "document"],
    "letter": ["bonafide", "noc", "document"],
    "pass": ["bonafide", "id card", "railway concession", "bus pass"],
    "map": ["floor", "room", "locator", "where", "location"],
    "where": ["map", "location", "floor", "locator"],
    "locate": ["map", "floor", "room", "locator"],
    "find": ["map", "locator", "floor"],
    "wifi": ["internet", "network", "amenities"],
    "internet": ["wifi", "network"],
    "parking": ["bike", "scooter", "car", "vehicle"],
    "print": ["xerox", "photocopy", "stationery"],
    "printing": ["xerox", "photocopy", "stationery"],
    "photocopy": ["xerox", "stationery"],
    "doctor": ["medical", "health", "sick", "hospital"],
    "sick": ["medical", "doctor", "health", "leave"],
    "fever": ["medical", "doctor", "sick"],
    "marks": ["passing marks", "grading", "cgpa", "sgpa"],
    "grade": ["grading", "passing marks", "cgpa"],
    "grades": ["grading", "passing marks", "cgpa"],
    "result": ["cgpa", "exam", "grading"],
    "holiday": ["vacation", "calendar", "diwali"],
    "holidays": ["vacation", "calendar", "diwali"],
    "vacation": ["holiday", "calendar", "diwali"],
    "uniform": ["dress code", "clothes", "decorum"],
    "dress": ["dress code", "uniform", "clothes"],
    "clothes": ["dress code", "uniform"],
}


def campus_brain(message, student=None):
    """
    Rich Offline Campus Intelligence Engine:
    Handles greetings, small-talk, leadership, daily amenities,
    academic policies, emergency contacts, and campus life reliably.
    """
    msg = message.lower().strip()
    words = set(re.findall(r"[a-zA-Z0-9\u0900-\u097F]+", msg))

    # 1. Greetings & Pleasantries
    greetings = ["hello", "hi", "hey", "namaste", "kem cho", "yo", "wassup", "sup"]
    if any(g == msg or msg.startswith(g + " ") for g in greetings):
        name_greet = f", {student['name'].split()[0]}" if student else ""
        return (
            f"👋 Hello{name_greet}! Welcome to **GH Raisoni International Skill Tech University Smart Campus Assistant**.\n\n"
            f"How can I assist you today? You can ask me:\n"
            f"• 🎯 *'Can I bunk?'* or *'What if I miss 2 classes today?'*\n"
            f"• 📊 *'My attendance'* or *'My CGPA'*\n"
            f"• 🪪 *'Show my ID card'*\n"
            f"• 📄 *'Generate Bonafide letter'*\n"
            f"• 📶 *'Campus WiFi'* or *'Parking rules'*\n"
            f"• 🗺️ *'Where is Accounts / Lab 302?'*",
            "Campus Assistant (Greeting)"
        )

    if any(t in msg for t in ["good morning", "good afternoon", "good evening", "shubh prabhat"]):
        name_greet = f", {student['name'].split()[0]}" if student else ""
        return (
            f"🌅 Good day{name_greet}! Welcome to GH Raisoni Campus Portal.\n\n"
            f"I'm here 24/7 to help you track your lecture attendance, view your 3D digital ID pass, "
            f"check exam schedules, fee dues, or navigate campus rooms.",
            "Campus Assistant (Greeting)"
        )

    if any(q in msg for q in ["how are you", "how r u", "kasa ahes", "kaise ho"]):
        return (
            "😊 I'm doing great, thank you for asking! Ready and standing by to assist you with all your "
            "academic queries, attendance forecasts, and campus facilities at GH Raisoni.",
            "Campus Assistant (Small Talk)"
        )

    if any(t in msg for t in ["thank you", "thanks", "thx", "dhanyawad", "shukriya"]):
        return (
            "🙏 You're very welcome! Feel free to ask anytime if you need help with attendance, "
            "bonafide certificates, exams, or campus locations. Have a productive day! 🎓",
            "Campus Assistant (Small Talk)"
        )

    if any(b in msg for b in ["bye", "goodbye", "see you", "tata", "alvida"]):
        return (
            "👋 Goodbye! Best wishes with your classes and studies. "
            "Remember to keep your attendance above 75%! Have a wonderful day!",
            "Campus Assistant (Small Talk)"
        )

    # 2. Identity & Authorship
    if any(q in msg for q in ["who are you", "what is your name", "what are you", "introduce yourself", "tell me about yourself"]):
        return (
            "🤖 **GH Raisoni Campus AI Smart Assistant** (Autonomous Cycle 2026–27):\n\n"
            "I am the official intelligent digital assistant for **GH Raisoni International Skill Tech University, Pune**.\n"
            "• **Key Capabilities:**\n"
            "  - 🎯 Real-time Lecture Bunk & Attendance Recovery Calculator (75% Rule)\n"
            "  - 🪪 3D Flippable Digital Student Identity Pass with QR & Barcode\n"
            "  - 📄 Instant Institutional Bonafide Certificate Generator\n"
            "  - 🗺️ Multi-Floor Indoor Campus Room & Lab Navigator\n"
            "  - 📚 Exam schedules, Fee balances, Faculty Mentors, and Canteen menus",
            "Campus Identity"
        )

    if any(q in msg for q in ["who made you", "who created you", "who developed you", "developer", "author", "creator", "project team", "kanishk"]):
        return (
            "👨‍💻 **PROJECT AUTHORS & DEVELOPMENT TEAM**:\n\n"
            "• **Developer:** **Kanishk Singh** (PRN: `ISTU25010120001`)\n"
            "• **Program:** BBA (Computer Applications), Semester III, Academic Year 2026–27\n"
            "• **Project Guide:** **Asst. Prof. Sheela Satav**\n"
            "• **Institution:** GH Raisoni International Skill Tech University, Wagholi Main Campus, Pune\n"
            "• **Hon'ble Vice Chancellor:** **Dr. R. D. Kharadkar**\n\n"
            "Built with Python Flask, SQLite, and 3D Modern CSS Web Standards.",
            "Developer & Credits"
        )

    # 3. Leadership & Key Faculty
    if any(q in msg for q in ["vice chancellor", "vc", "kharadkar", "rd kharadkar", "chancellor"]):
        return (
            "🏛️ **UNIVERSITY LEADERSHIP**:\n\n"
            "• **Hon'ble Vice Chancellor:** **Dr. R. D. Kharadkar**\n"
            "• **Institution:** GH Raisoni International Skill Tech University, Pune\n"
            "• **Vice Chancellor's Office:** Admin Building, 2nd Floor, Wagholi Main Campus, Pune.",
            "University Leadership"
        )

    if any(q in msg for q in ["sheela satav", "satav", "project guide"]):
        return (
            "👩‍🏫 **PROJECT GUIDE & FACULTY COORDINATOR**:\n\n"
            "• **Faculty Name:** **Asst. Prof. Sheela Satav**\n"
            "• **Designation:** Assistant Professor, Department of Computer Applications\n"
            "• **Role:** Project Guide for BBA (CA) Semester III Academic Capstone Projects\n"
            "• **Cabin / Location:** Faculty Cabin 204, Academic Block, Wagholi Campus.",
            "Faculty Coordinator"
        )

    if any(q in msg for q in ["hod", "head of department"]):
        return (
            "👨‍🏫 **HEAD OF DEPARTMENT (HOD)**:\n\n"
            "• **BBA (Computer Applications) / BCA:** **Dr. A. Sharma** (HOD Office: Room 304, Academic Block)\n"
            "• **Mentoring & Consultation Hours:** 2:00 PM – 4:30 PM (Daily)",
            "Department Leadership"
        )

    # 4. Daily Campus Facilities
    if any(k in msg for k in ["wifi", "wi-fi", "internet", "network password"]):
        return (
            "📶 **CAMPUS HIGH-SPEED WI-FI ACCESS**:\n\n"
            "• **SSID Network:** `GHR-Campus-5G` or `GHR-Student-WiFi`\n"
            "• **Authentication:** Login using your official Student PRN (Registration No) and Portal Password.\n"
            "• **Coverage:** High-density access points across Classrooms, Central Library, Computer Labs, Canteen, and Hostels.\n"
            "• **Assistance:** IT Helpdesk & Server Room 104 (Ground Floor Admin Block).",
            "Campus Facilities"
        )

    if any(k in msg for k in ["parking", "bike", "scooter", "car parking", "vehicle"]):
        return (
            "🅿️ **CAMPUS PARKING GUIDELINES**:\n\n"
            "• **Two-Wheelers (Bikes/Scooters):** Dedicated shaded student parking bays beside Gate 1 & Gate 2. Parking tag sticker issued by Security Gate 1.\n"
            "• **Four-Wheelers:** Reserved faculty & visitor parking lot in front of Admin Block.\n"
            "• **Rules:** Speed limit 15 km/h inside campus; helmets mandatory at entry gate.",
            "Campus Facilities"
        )

    if any(k in msg for k in ["xerox", "photocopy", "print", "printing", "stationery", "spiral binding"]):
        return (
            "🖨️ **XEROX & REPROGRAPHICS CENTER**:\n\n"
            "• **Locations:**\n"
            "  1. Ground Floor Student Amenity Counter (Directly opposite Main Canteen)\n"
            "  2. Admin Block Basement (Behind Central Store)\n"
            "• **Services:** High-speed Xerox (₹1/page), Color Printouts, Spiral / Hard Binding for Project Reports, and academic stationery.\n"
            "• **Hours:** 8:30 AM – 6:00 PM (Monday to Saturday).",
            "Campus Amenities"
        )

    if any(k in msg for k in ["dress code", "uniform", "what to wear", "clothes", "attire", "jeans", "wear"]):
        return (
            "👔 **CAMPUS DRESS CODE & DECORUM**:\n\n"
            "• **Regular Days:** Decent, neat smart-casual attire.\n"
            "• **Formal Days (Mondays & Presentation Sessions):** Official Formals (College blazer or formal shirt/trousers).\n"
            "• **Mandatory Rule:** **Student Identity Card must be visibly worn around the neck at all times** while on campus and during lectures/practicals.",
            "Campus Discipline"
        )

    if any(k in msg for k in ["medical", "doctor", "sick", "fever", "illness", "first aid", "health center", "hospital"]):
        return (
            "🏥 **CAMPUS MEDICAL CENTER & HEALTHCARE**:\n\n"
            "• **Location:** Ground Floor, Admin Block (Room 108).\n"
            "• **Facilities:** First Aid, Emergency Doctor on-call, Registered Nurse on duty (9 AM – 5 PM), and ambulance standby.\n"
            "• **Emergency Desk:** +91 20-67528000 (Ext. 108).\n"
            "• **Medical Leave Policy:** If absent due to medical reasons, submit an authentic MBBS Doctor's certificate to Admin Counter 4 within 48 hours for attendance consideration.",
            "Campus Healthcare"
        )

    # 5. Academic Rules & Regulations
    if any(k in msg for k in ["passing marks", "passing criteria", "pass percentage", "minimum marks", "passing percentage"]):
        return (
            "📊 **PASSING CRITERIA & EVALUATION SCHEME**:\n\n"
            "• **Subject Passing:** Minimum **40% marks** required separately in Internal Assessment and External University Theory Examination.\n"
            "• **Internal Assessment (40 Marks):** Mid-term tests, assignments, seminar presentations, and attendance mark component.\n"
            "• **External Exam (60 Marks):** End-semester university theory paper.\n"
            "• **Grading:** 10-Point CBCS Scale (O: 90+, A+: 80+, A: 70+, B+: 60+, B: 55+, C: 50+, P: 40+, F: Fail).",
            "Academic Regulations"
        )

    if any(k in msg for k in ["backlog", "kt", "atkt", "arrear", "fail", "re-exam"]):
        return (
            "📝 **ATKT & BACKLOG EXAMINATION RULES**:\n\n"
            "• Students may carry forward a maximum of 4 backlogs to the next academic year under university ATKT progression rules.\n"
            "• Backlog papers are scheduled alongside the regular semester examinations.\n"
            "• Backlog exam fee forms must be submitted online via the student ERP portal or at Counter 4 before the declared deadline.",
            "Academic Regulations"
        )

    if any(k in msg for k in ["holiday", "holidays", "vacation", "diwali", "calendar", "academic calendar"]):
        return (
            "📅 **ACADEMIC CALENDAR & HOLIDAYS (2026–27)**:\n\n"
            "• **Active Semester:** Semester III (August – December 2026)\n"
            "• **Mid-Term Examination:** October 2026\n"
            "• **Diwali Vacation:** Announced via official circular on ERP portal (10 days)\n"
            "• **End Semester Exams:** Commencing 10-Dec-2026\n"
            "• **Weekly Off:** Sundays and 2nd/4th Saturdays.",
            "Academic Calendar"
        )

    if any(k in msg for k in ["lost id", "lost my id", "duplicate id", "id lost"]):
        return (
            "🪪 **LOST ID CARD PROCEDURE**:\n\n"
            "1. Report the lost card immediately to Security Gate 1 & Admin Counter 4.\n"
            "2. Fill out the Duplicate ID Card Requisition Form.\n"
            "3. Pay nominal re-issue fee (₹100) at Accounts Counter 4.\n"
            "4. Your new physical smart card will be ready within 2 business days.\n\n"
            "💡 In the meantime, use your **3D Digital ID Pass** inside this chatbot as temporary verified campus ID!\n"
            "<button class='action-pill-btn' onclick='openIdCardModal()'>✨ Open 3D Digital Pass</button>",
            "Student Services"
        )

    # 6. Humor & Motivation
    if any(k in msg for k in ["joke", "make me laugh", "tell me a joke", "funny"]):
        return (
            "😄 *Why did the computer science student attend all his lectures on time?*\n\n"
            "Because he heard the college had a strict 75% cache hit rate! 🚀\n"
            "Remember, don't 404 on your attendance!",
            "Small Talk (Humor)"
        )

    if any(k in msg for k in ["motivate", "motivation", "quote", "inspire"]):
        return (
            "🌟 *'Success doesn't come from what you do occasionally, it comes from what you do consistently.'*\n\n"
            "Stay regular with your lectures, maintain 75%+ attendance, and you'll ace your semester exams at GH Raisoni! 🎓💪",
            "Small Talk (Motivation)"
        )

    return None, None


def smart_fallback_response(message, student=None):
    """
    Intelligent campus fallback with dynamic action pill suggestions.
    """
    name = f" {student['name'].split()[0]}" if student else ""
    return (
        f"I couldn't find a direct campus FAQ match for: *\"{message}\"*.\n\n"
        f"As the official **GH Raisoni Campus Smart Assistant**, I can directly help you with:\n"
        f"• 🎯 **Attendance & Bunk Simulator**: Ask *'What if I miss 2 classes today?'* or *'Can I bunk?'*\n"
        f"• 📊 **Live Student Records**: Check real-time attendance percentage, CGPA, and pending fee balance\n"
        f"• 🪪 **Digital ID Pass**: Access your 3D flippable institutional identity card\n"
        f"• 📄 **Bonafide Certificates**: Preview and print official college letterhead drafts\n"
        f"• 🏛️ **Campus Amenities**: Wi-Fi login, parking rules, library hours, canteen menu, and medical center\n"
        f"• 🗺️ **Floor Navigator**: Locate classrooms, seminar halls, and computer labs across all 4 floors\n\n"
        f"👉 **Quick Action Tools:**\n"
        f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Bunk Calculator</button> "
        f"<button class='action-pill-btn' onclick='openIdCardModal()'>🪪 Digital ID Pass</button> "
        f"<button class='action-pill-btn' onclick='openBonafideModal()'>📄 Bonafide Draft</button> "
        f"<button class='action-pill-btn' onclick='openMapModal()'>🗺️ Floor Map</button>\n\n"
        f"*(For in-person support, visit Central Admin Counter 4 or call Campus Security at +91 20-67528000)*"
    )


def match_query(message):
    """
    Rule-based NLP with typo tolerance and synonym expansion.
    Returns (answer, category) or (None, None).
    """
    message_lower = message.lower()
    words = set(re.findall(r"[a-zA-Z0-9\u0900-\u097F]+", message_lower))

    # Common stop-words that shouldn't trigger accidental fuzzy matches
    STOP_WORDS = {"on", "in", "at", "to", "for", "of", "with", "by", "from", "is", "are", "was", "were", "a", "an", "the", "i", "you", "he", "she", "it", "we", "they"}
    content_words = words - STOP_WORDS

    expanded_words = set(content_words)
    for w in content_words:
        if w in SYNONYM_MAP:
            expanded_words.update(SYNONYM_MAP[w])

    conn = get_db()
    rows = conn.execute("SELECT category, keywords, answer FROM college_info").fetchall()
    conn.close()

    best_row = None
    best_score = 0
    had_exact = False

    for row in rows:
        keywords = [k.strip().lower() for k in row["keywords"].split(",") if k.strip()]
        score = 0
        exact_in_category = False

        for kw in keywords:
            # Multi-word exact match
            if " " in kw and kw in message_lower:
                score += 3
                exact_in_category = True
            elif kw in content_words:
                score += 2
                exact_in_category = True
            else:
                kw_parts = set(kw.split()) - STOP_WORDS
                if not kw_parts:
                    continue
                overlap = kw_parts.intersection(expanded_words)
                if len(overlap) == len(kw_parts):
                    score += 2
                    exact_in_category = True
                elif overlap and len(overlap) >= 1:
                    score += 1
                elif len(kw) >= 5:
                    for kp in kw_parts:
                        if len(kp) >= 5 and difflib.get_close_matches(kp, list(content_words), n=1, cutoff=0.88):
                            score += 1
                            break

        if score > best_score:
            best_score = score
            best_row = row
            had_exact = exact_in_category

    # If only matched fuzzily without any exact or synonym match, require threshold >= 3
    min_threshold = 2 if had_exact else 3
    if best_row and best_score >= min_threshold:
        return best_row["answer"], best_row["category"]

    return None, None


def get_categories():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT category FROM college_info ORDER BY id").fetchall()
    conn.close()
    return [r["category"] for r in rows]


def personalized_answer(message, roll_no):
    """
    If a logged-in student asks about their personal records,
    fetch their specific record instead of the generic FAQ answer.
    """
    msg = message.lower()
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
    ).fetchone()
    conn.close()

    if not student:
        return None

    att = float(student["attendance"])
    total_conducted = 60
    attended = int(round((att / 100.0) * total_conducted))

    # 1. ATTENDANCE WHAT-IF / MISSING LECTURES SIMULATOR
    # (Matches: "i will not attend 2 classes today ?", "what if I miss 1 class", "if i skip 3 lectures", "cannot attend", "absent today", "take leave", "bunk 2 classes")
    miss_patterns = [
        r"(?:not|won'?t|cannot|can'?t|dont|don'?t)\s+(?:attend|come|go)",
        r"(?:miss|missing|skip|skipping|bunk|bunking)",
        r"(?:absent|leave|off)\s+today",
        r"(?:take|taking)\s+leave",
        r"not\s+(?:coming|going|attending)",
    ]
    if any(re.search(p, msg) for p in miss_patterns) and any(w in msg for w in ["class", "classes", "lecture", "lectures", "period", "periods", "today", "tomorrow"]):
        num_match = re.search(r"(\d+)\s*(?:classes|class|lectures|lecture|periods|period|hours|hour)?", msg)
        word_nums = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "half": 2}

        miss_count = None
        if num_match:
            miss_count = int(num_match.group(1))
        else:
            for w, val in word_nums.items():
                if w in msg:
                    miss_count = val
                    break

        if miss_count is None:
            miss_count = 2 if any(w in msg for w in ["classes", "lectures", "periods"]) else 1

        miss_count = max(1, min(miss_count, 15))
        new_total = total_conducted + miss_count
        new_attended = attended
        new_pct = round((new_attended / new_total) * 100, 2)
        diff_pct = round(att - new_pct, 2)

        if new_pct >= 75.0:
            safe_remaining = int(math.floor((new_attended / 0.75) - new_total))
            safe_remaining = max(0, safe_remaining)
            return (
                f"🎯 **ATTENDANCE IMPACT SIMULATOR FOR {student['name'].upper()}**:\n\n"
                f"• Current Attendance: **{att}%** ({attended}/{total_conducted} conducted lectures attended)\n"
                f"• **If you miss {miss_count} lecture(s) today:**\n"
                f"  - Total Conducted: {total_conducted} ➔ **{new_total}**\n"
                f"  - Your Attended: {attended} ➔ **{new_attended}**\n"
                f"  - Projected Attendance: **{new_pct}%** (drops by {diff_pct}%)\n"
                f"• Standing: ✅ **SAFE / GOOD STANDING** (Above 75% cutoff)\n"
                f"• Safe Buffer: You can still safely miss up to **{safe_remaining} more lecture(s)** afterwards!\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                "Attendance Simulator"
            )
        elif att >= 75.0 and new_pct < 75.0:
            return (
                f"🚨 **ATTENDANCE SHORTAGE RISK FOR {student['name'].upper()}**:\n\n"
                f"• Current Attendance: **{att}%** ({attended}/{total_conducted} conducted lectures attended)\n"
                f"• **If you miss {miss_count} lecture(s) today:**\n"
                f"  - Total Conducted: {total_conducted} ➔ **{new_total}**\n"
                f"  - Your Attended: {attended} ➔ **{new_attended}**\n"
                f"  - Projected Attendance: **{new_pct}%** (drops by {diff_pct}%)\n"
                f"• Standing: ⚠️ **DROPS BELOW 75% MANDATORY CUTOFF!**\n"
                f"• Warning: Missing {miss_count} lecture(s) today pushes you into the detention warning bracket!\n"
                f"• Recommendation: 🛑 **Do NOT miss classes today.** Maintain your exam eligibility!\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                "Attendance Alert"
            )
        else:
            needed = int(math.ceil(((0.75 * new_total) - new_attended) / 0.25))
            needed = max(1, needed)
            return (
                f"🚨 **ATTENDANCE SHORTAGE ALERT FOR {student['name'].upper()}**:\n\n"
                f"• Current Attendance: **{att}%** ({attended}/{total_conducted} conducted lectures attended)\n"
                f"  *(Note: You are already in the detention warning bracket below 75%)*\n"
                f"• **If you miss {miss_count} lecture(s) today:**\n"
                f"  - Total Conducted: {total_conducted} ➔ **{new_total}**\n"
                f"  - Your Attended: {attended} ➔ **{new_attended}**\n"
                f"  - Projected Attendance: **{new_pct}%** (drops by {diff_pct}%)\n"
                f"• Impact: ❌ **Deepens your detention shortage!**\n"
                f"• Recovery Target: After missing today, you must attend **{needed} consecutive lectures** with 0 absences to climb back to 75%.\n"
                f"• Faculty Mentor: Contact **{student['mentor']}** at Admin Block Counter 4.\n"
                f"• Urgent Advice: 🛑 We strongly advise attending all lectures today. If medically unwell, submit a registered doctor certificate within 48 hours.\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                "Detention Alert"
            )

    # 2. Full profile summary
    if any(q in msg for q in ["profile", "who am i", "my details", "about me", "my info", "student info"]):
        fee_status = (
            f"Rs {student['fees_due']:.0f} pending"
            if student["fees_due"] and student["fees_due"] > 0
            else "All cleared (No dues)"
        )
        return (
            f"👤 STUDENT PROFILE SUMMARY:\n\n"
            f"• Full Name: {student['name']}\n"
            f"• Registration No: {student['roll_no']}\n"
            f"• Program: {student['course']} ({student['semester']})\n"
            f"• Cumulative GPA (CGPA): {student['cgpa']} / 10.0\n"
            f"• Lecture Attendance: {student['attendance']}%\n"
            f"• Fee Balance: {fee_status}\n"
            f"• Faculty Mentor: {student['mentor']}\n"
            f"• Next Exam Date: {student['exam_date']}\n\n"
            f"💡 Tip: Tap 'My ID Card' to view your 3D digital pass or ask 'Can I bunk?' for your safe attendance margin.",
            "Student Profile"
        )

    # 3. Smart Attendance & Bunk Target Calculator
    if any(k in msg for k in ["bunk", "miss class", "skip class", "attendance target", "target attendance", "can i bunk", "how many bunk"]) or (
        "how many" in msg and any(k in msg for k in ["class", "lecture", "attend"])
    ):
        if att >= 75.0:
            bunkable = int(math.floor((attended / 0.75) - total_conducted))
            bunkable = max(0, bunkable)
            if bunkable > 0:
                new_pct = round((attended / (total_conducted + bunkable)) * 100, 1)
                return (
                    f"🎯 SMART BUNK CALCULATOR for {student['name']}:\n\n"
                    f"• Current Attendance: {att}% ({attended}/{total_conducted} conducted lectures attended)\n"
                    f"• Academic Standing: ✅ Safe / Good Standing (Above 75%)\n"
                    f"• Safe Bunks Margin: You can safely miss up to **{bunkable} lecture(s)** and still remain above 75%! 🎉\n"
                    f"• Forecast: After bunking {bunkable} classes, your attendance will be approximately {new_pct}%.\n\n"
                    f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                    "Bunk Calculator"
                )
            else:
                return (
                    f"🎯 SMART BUNK CALCULATOR for {student['name']}:\n\n"
                    f"• Current Attendance: {att}% ({attended}/{total_conducted} conducted lectures attended)\n"
                    f"• Status: ⚠️ Right at 75% Boundary\n"
                    f"• Safe Bunk Margin: **0 classes**. Missing even 1 single lecture will push you below 75% and trigger the detention bracket!\n\n"
                    f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                    "Bunk Calculator"
                )
        else:
            needed = int(math.ceil(((0.75 * total_conducted) - attended) / 0.25))
            needed = max(1, needed)
            new_pct = round(((attended + needed) / (total_conducted + needed)) * 100, 1)
            return (
                f"🚨 ATTENDANCE RECOVERY & BUNK ALERT for {student['name']}:\n\n"
                f"• Current Attendance: {att}% ({attended}/{total_conducted} conducted lectures attended)\n"
                f"• Can you bunk? **Strictly NO. You are currently in a detention shortage bracket.**\n"
                f"• Recovery Target: You must attend **{needed} consecutive lectures** without missing any to reach the safe 75% threshold.\n"
                f"• Forecast: Attending {needed} more classes will bring your attendance to {new_pct}%.\n"
                f"• Detention Action: Review the required assignments or prelims with HOD ({student['mentor']}).\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Attendance Recovery Calculator</button>",
                "Attendance Recovery"
            )

    # 4. Bonafide / NOC Certificate
    if any(k in msg for k in ["bonafide", "certificate", "noc", "document draft", "bus pass", "railway concession"]):
        return (
            f"📄 OFFICIAL DIGITAL BONAFIDE & DOCUMENT PORTAL:\n\n"
            f"Verified Student Record: {student['name']} ({student['roll_no']})\n"
            f"Program: {student['course']}, {student['semester']}\n\n"
            f"Your institutional Bonafide Certificate draft is ready for instant viewing and printing!\n\n"
            f"👉 Tap the button below to preview your official college letterhead draft:\n"
            f"<button class='action-pill-btn' onclick='openBonafideModal()'>📜 View & Print Official Bonafide</button>",
            "Bonafide Service"
        )

    # 5. Digital Student ID Card (excludes lost/duplicate report queries)
    if ("lost" not in msg and "duplicate" not in msg) and any(k in msg for k in ["id card", "digital id", "my id", "student card", "campus pass", "identity card"]):
        return (
            f"🪪 DIGITAL STUDENT IDENTITY CARD:\n\n"
            f"Digital campus identity credentials for {student['name']} ({student['roll_no']}) are ready.\n"
            f"Features: 3D Flip, Live Verification QR Code, and Barcode.\n\n"
            f"👉 <button class='action-pill-btn' onclick='openIdCardModal()'>✨ Open 3D Digital Student ID Card</button>",
            "Digital ID Pass"
        )

    # 6. Attendance with official 4-tier College Detention Policy
    if "attendance" in msg or any(k in msg for k in ["hajeri", "hazari", "upasthiti", "present", "shortage"]):
        if att >= 75.0:
            status = "✅ Good Standing — Fully eligible for semester examinations"
            advice = "Your attendance is in good standing. Keep maintaining it above 75%!"
        elif 60.0 <= att < 75.0:
            status = "⚠️ Detention Warning (60% to 75% Bracket)"
            advice = (
                "Under the college detention policy rubrics, you must complete the following to clear detention:\n"
                "• Theory: End Sem Examination Paper Sets of previous 2 years must be solved in Open Book mode in the College.\n"
                "• Practical: You will not be eligible for the attendance mark component of internal marks."
            )
        elif 50.0 <= att < 60.0:
            status = "🚨 Critical Detention Shortage (50% to 59.99% Bracket)"
            advice = (
                "Under official detention policy rubrics, you are detained unless you complete:\n"
                "• Theory: (1) End Sem Examination Paper Sets of previous 2 years must be solved in Open Book mode in the College, AND (2) Appear for a prelim examination and score a minimum of 60% marks to be eligible to get out of detention.\n"
                "• Practical: Appear for a practical-based prelim examination and score a minimum of 60% marks (Max 2 practicals conducted in a day)."
            )
        else:
            status = "❌ Strictly Detained (<50% Attendance)"
            advice = "As per college detention policy, students with attendance below 50% have No Consideration and are strictly detained from university semester examinations. Contact your HOD immediately."

        return (
            f"Hi {student['name']}, your current attendance is {att}% ({status}).\n\n"
            f"📋 College Rubrics & Action Required:\n{advice}\n\n"
            f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Calculator</button>",
            "Student Attendance"
        )

    # 7. Fees
    if any(k in msg for k in ["fee", "fees", "dues", "balance", "pending", "shulk", "shulka"]):
        due = student["fees_due"]
        if due and due > 0:
            return (
                f"Hi {student['name']}, you have Rs {due:.0f} in pending fees. You can pay online via the student ERP portal or at Accounts Counter 4.",
                "Fee Status"
            )
        return f"Hi {student['name']}, you have no pending fees. You're completely all clear! 🎉", "Fee Status"

    # 8. Exams
    if any(k in msg for k in ["exam", "exams", "datesheet", "timetable", "pariksha"]):
        return (
            f"Hi {student['name']}, your next semester examination begins on {student['exam_date']}. Admit cards are downloadable from the student portal exactly 7 days before commencement.",
            "Exam Schedule"
        )

    # 9. CGPA / Marks / Results (excludes generic passing criteria queries)
    if ("passing" not in msg and "pass mark" not in msg and "cutoff" not in msg) and any(k in msg for k in ["cgpa", "sgpa", "gpa", "marks", "result", "grade", "score", "gun", "pointer"]):
        return (
            f"Hi {student['name']}, your current CGPA is {student['cgpa']} / 10.0 in {student['course']} ({student['semester']}). Keep up the great work! 🌟",
            "Student CGPA"
        )

    # 10. Mentor / Guide
    if any(k in msg for k in ["mentor", "guide", "counselor", "class teacher"]):
        return (
            f"Hi {student['name']}, your designated faculty mentor is {student['mentor']}. You can contact them during mentoring hours or via email.",
            "Faculty Mentor"
        )

    # 11. Course / Semester
    if any(k in msg for k in ["course", "semester", "branch", "program"]):
        return (
            f"Hi {student['name']}, you are currently registered in {student['course']}, {student['semester']}.",
            "Course Info"
        )

    return None


# ---------------- ROUTES: CHAT UI ----------------

@app.route("/")
def home():
    roll_no = session.get("roll_no")
    student_record = None
    if roll_no:
        conn = get_db()
        student_record = conn.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,)).fetchone()
        conn.close()

    return render_template(
        "index.html",
        student_name=session.get("student_name"),
        student=student_record,
        categories=get_categories(),
    )


@app.route("/service-worker.js")
def service_worker():
    # Served from the root path so its scope covers the whole site for PWA
    response = send_from_directory("static", "service-worker.js")
    response.headers["Service-Worker-Allowed"] = "/"
    return response


@app.route("/docs/uml")
def docs_uml():
    return send_from_directory("docs", "UML_DIAGRAMS.html")


@app.route("/docs/dfd")
def docs_dfd():
    return send_from_directory("docs", "DFD_DIAGRAM.html")


@app.route("/docs/erd")
def docs_erd():
    return send_from_directory("docs", "ERD_DIAGRAM.html")


@app.route("/docs/report")
def docs_report():
    return send_from_directory("docs", "PROJECT_REPORTS.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"response": "Please type a question or use voice input."})

    roll_no = session.get("roll_no")
    student = None
    if roll_no:
        conn = get_db()
        student = conn.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,)).fetchone()
        conn.close()

    bot_response = None
    category = None
    source = "Knowledge Base"

    # Tier 1: Check personalized student queries (Simulation, Attendance, CGPA, ID, etc.)
    if roll_no and student:
        resp = personalized_answer(user_message, roll_no)
        if resp:
            if isinstance(resp, tuple):
                bot_response, category = resp
            else:
                bot_response, category = resp, "Personalized Portal"
            source = "Student Database"

    # Tier 2: Check rich Campus Brain (Leadership, Facilities, Wifi, Parking, Greetings, About, etc.)
    if not bot_response:
        resp = campus_brain(user_message, student)
        if resp and resp[0]:
            bot_response, category = resp
            source = "Campus Intelligence"

    # Tier 3: Check FAQ Knowledge Base (SQL college_info with fuzzy synonym expansion)
    if not bot_response:
        ans, cat = match_query(user_message)
        if cat:
            bot_response, category = ans, cat
            source = "Knowledge Base"

    # Tier 4: Check Google Gemini AI Hybrid (if API key available)
    if not bot_response:
        gemini_ans = ask_gemini(user_message)
        if gemini_ans:
            bot_response = f"{gemini_ans}\n\n*(🤖 Verified Campus AI Hybrid)*"
            category = "Campus AI (Gemini)"
            source = "Gemini Hybrid"

    # Tier 5: Smart Contextual Fallback with Action Buttons
    if not bot_response:
        bot_response = smart_fallback_response(user_message, student)
        category = "Campus Support"
        source = "Campus Assistant"

    # Save to chat history and capture ID
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (roll_no, user_query, bot_response) VALUES (?, ?, ?)",
        (roll_no, user_message, bot_response),
    )
    history_id = cur.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "response": bot_response,
        "category": category,
        "source": source,
        "history_id": history_id
    })


@app.route("/api/student/info")
def student_info():
    roll_no = session.get("roll_no")
    if not roll_no:
        return jsonify({"error": "Unauthorized"}), 401
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,)).fetchone()
    conn.close()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dict(student))


@app.route("/api/calculate_bunk", methods=["POST"])
def api_calculate_bunk():
    data = request.get_json() or {}
    try:
        total = int(data.get("total", 60))
        attended = int(data.get("attended", 45))
        target = float(data.get("target", 75.0))
        
        if total <= 0:
            return jsonify({"error": "Total lectures must be greater than 0"}), 400
        if attended > total:
            return jsonify({"error": "Attended lectures cannot exceed total lectures"}), 400

        current_pct = round((attended / total) * 100, 2)
        target_dec = target / 100.0

        if current_pct >= target:
            # Safe bunks: attended / (total + x) >= target_dec
            bunkable = int(math.floor((attended / target_dec) - total))
            bunkable = max(0, bunkable)
            forecast_pct = round((attended / (total + bunkable)) * 100, 2) if bunkable > 0 else current_pct
            return jsonify({
                "status": "safe",
                "current_percentage": current_pct,
                "can_bunk": True,
                "bunks_allowed": bunkable,
                "forecast_percentage": forecast_pct,
                "message": f"You can safely miss up to {bunkable} lecture(s) while maintaining >= {target}%."
            })
        else:
            # Consecutive classes needed: (attended + y) / (total + y) >= target_dec
            needed = int(math.ceil(((target_dec * total) - attended) / (1 - target_dec)))
            needed = max(1, needed)
            forecast_pct = round(((attended + needed) / (total + needed)) * 100, 2)
            return jsonify({
                "status": "shortage",
                "current_percentage": current_pct,
                "can_bunk": False,
                "lectures_needed": needed,
                "forecast_percentage": forecast_pct,
                "message": f"Shortage detected! You must attend {needed} consecutive lectures to reach {target}%."
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/chat/feedback", methods=["POST"])
def chat_feedback():
    data = request.get_json() or {}
    history_id = data.get("history_id")
    rating = data.get("rating")  # "like" or "dislike"

    if history_id and rating in ["like", "dislike"]:
        conn = get_db()
        conn.execute("UPDATE chat_history SET feedback = ? WHERE id = ?", (rating, history_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "history_id": history_id, "rating": rating})

    return jsonify({"status": "ignored"}), 400


# ---------------- ROUTES: STUDENT LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip().upper()

        if not roll_no.startswith("ISTU"):
            return render_template(
                "login.html",
                error="Registration number should start with ISTU (e.g. ISTU00000001).",
            )

        conn = get_db()
        student = conn.execute(
            "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
        ).fetchone()
        conn.close()

        if student:
            session["roll_no"] = student["roll_no"]
            session["student_name"] = student["name"]
            return redirect(url_for("home"))
        else:
            error = "Registration number not found. Please check and try again."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("roll_no", None)
    session.pop("student_name", None)
    return redirect(url_for("home"))


# ---------------- ROUTES: ADMIN PANEL ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if admin and check_password_hash(admin["password_hash"], password):
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("admin_login.html", error=error)


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()
    faqs = conn.execute("SELECT * FROM college_info ORDER BY category").fetchall()
    history = conn.execute(
        "SELECT * FROM chat_history ORDER BY id DESC LIMIT 100"
    ).fetchall()
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_chats = conn.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]
    
    # Identify queries where bot gave fallback (potential missing FAQs)
    unanswered = conn.execute(
        "SELECT user_query, COUNT(*) as count FROM chat_history "
        "WHERE bot_response LIKE '%not completely sure%' "
        "GROUP BY user_query ORDER BY count DESC LIMIT 5"
    ).fetchall()
    conn.close()

    gemini_active = bool(os.environ.get("GEMINI_API_KEY", "").strip())

    return render_template(
        "admin_dashboard.html",
        faqs=faqs,
        history=history,
        total_faqs=len(faqs),
        total_chats=total_chats,
        total_students=total_students,
        unanswered=unanswered,
        gemini_active=gemini_active,
    )


@app.route("/admin/export_chat")
def admin_export_chat():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()
    rows = conn.execute(
        "SELECT id, roll_no, user_query, bot_response, timestamp, feedback FROM chat_history ORDER BY id DESC"
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Registration No", "User Query", "Bot Response", "Timestamp", "Feedback"])
    for r in rows:
        writer.writerow([
            r["id"],
            r["roll_no"] or "Guest",
            r["user_query"],
            r["bot_response"],
            r["timestamp"],
            r["feedback"] or "-",
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=college_chatbot_logs.csv"},
    )


@app.route("/admin/add", methods=["POST"])
def admin_add():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    category = request.form.get("category", "").strip()
    keywords = request.form.get("keywords", "").strip()
    answer = request.form.get("answer", "").strip()

    if category and keywords and answer:
        conn = get_db()
        conn.execute(
            "INSERT INTO college_info (category, keywords, answer) VALUES (?, ?, ?)",
            (category, keywords, answer),
        )
        conn.commit()
        conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete/<int:faq_id>", methods=["GET", "POST"])
def admin_delete(faq_id):
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()
    conn.execute("DELETE FROM college_info WHERE id = ?", (faq_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/change_password", methods=["POST"])
def admin_change_password():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    new_password = request.form.get("new_password", "").strip()
    if new_password:
        conn = get_db()
        conn.execute(
            "UPDATE admin SET password_hash = ? WHERE username = ?",
            (generate_password_hash(new_password), "admin"),
        )
        conn.commit()
        conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
