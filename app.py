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


# ---------------- CHATBOT LOGIC (rule-based keyword matching with fuzzy fallback) ----------------

def match_query(message):
    """
    Rule-based NLP with typo tolerance:
    1. Exact substring match against each category's keyword list.
    2. Fuzzy match against individual words in the message using difflib.
    Returns (answer, category) or a fallback message if nothing matches.
    """
    message_lower = message.lower()
    words = re.findall(r"[a-zA-Z0-9\u0900-\u097F]+", message_lower)

    conn = get_db()
    rows = conn.execute("SELECT category, keywords, answer FROM college_info").fetchall()
    conn.close()

    best_row = None
    best_score = 0

    for row in rows:
        keywords = [k.strip().lower() for k in row["keywords"].split(",") if k.strip()]
        score = 0
        for kw in keywords:
            if kw in message_lower:
                # Multi-word exact matches carry higher confidence
                score += 3 if " " in kw else 2
            else:
                kw_parts = kw.split()
                if len(kw_parts) == 1:
                    close = difflib.get_close_matches(kw, words, n=1, cutoff=0.80)
                    if close:
                        score += 1
                else:
                    # If multi-word keyword, check token overlap
                    matched_parts = sum(
                        1 for p in kw_parts
                        if p in words or difflib.get_close_matches(p, words, n=1, cutoff=0.82)
                    )
                    if matched_parts == len(kw_parts):
                        score += 2

        if score > best_score:
            best_score = score
            best_row = row

    if best_row and best_score >= 2:
        return best_row["answer"], best_row["category"]

    return (
        "I'm not completely sure about that. You can ask me about Admissions, "
        "Fee Structure, Exam Timetable, Attendance Rules, Placements, Hostels, "
        "Canteen Menu, Campus Map, or Bonafide Certificates — or tap one of the suggested topics below.",
        None,
    )


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

    # Full profile summary
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
            f"💡 Tip: Tap 'My ID Card' to view your 3D digital pass or ask 'Can I bunk?' for your safe attendance margin."
        )

    # Smart Attendance & Bunk Target Calculator
    if any(k in msg for k in ["bunk", "miss class", "skip class", "attendance target", "target attendance", "can i bunk", "how many bunk"]) or (
        "how many" in msg and any(k in msg for k in ["class", "lecture", "attend"])
    ):
        att = student["attendance"]
        total_conducted = 60
        attended = int(round((att / 100.0) * total_conducted))

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
                    f"💡 Click the '🎯 Bunk Tool' in the top bar to simulate custom lecture scenarios."
                )
            else:
                return (
                    f"🎯 SMART BUNK CALCULATOR for {student['name']}:\n\n"
                    f"• Current Attendance: {att}% ({attended}/{total_conducted} conducted lectures attended)\n"
                    f"• Status: ⚠️ Right at 75% Boundary\n"
                    f"• Safe Bunk Margin: **0 classes**. Missing even 1 single lecture will push you below 75% and trigger the detention bracket!"
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
                f"• Detention Action: Review the required assignments or prelims with HOD ({student['mentor']})."
            )

    # Bonafide / NOC Certificate
    if any(k in msg for k in ["bonafide", "certificate", "noc", "document draft", "bus pass", "railway concession"]):
        return (
            f"📄 OFFICIAL DIGITAL BONAFIDE & DOCUMENT PORTAL:\n\n"
            f"Verified Student Record: {student['name']} ({student['roll_no']})\n"
            f"Program: {student['course']}, {student['semester']}\n\n"
            f"Your institutional Bonafide Certificate draft is ready for instant viewing and printing!\n\n"
            f"👉 Tap the button below to preview your official college letterhead draft:\n"
            f"<button class='action-pill-btn' onclick='openBonafideModal()'>📜 View & Print Official Bonafide</button>"
        )

    # Digital Student ID Card
    if any(k in msg for k in ["id card", "digital id", "my id", "student card", "campus pass", "identity card"]):
        return (
            f"🪪 DIGITAL STUDENT IDENTITY CARD:\n\n"
            f"Digital campus identity credentials for {student['name']} ({student['roll_no']}) are ready.\n"
            f"Features: 3D Flip, Live Verification QR Code, and Barcode.\n\n"
            f"👉 <button class='action-pill-btn' onclick='openIdCardModal()'>✨ Open 3D Digital Student ID Card</button>"
        )

    # Attendance with official 4-tier College Detention Policy
    if "attendance" in msg and any(k in msg for k in ["my", "what", "how", "current", "show", "hajeri", "hazari"]):
        att = student["attendance"]
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
        else:  # < 50.0
            status = "❌ Strictly Detained (<50% Attendance)"
            advice = "As per college detention policy, students with attendance below 50% have No Consideration and are strictly detained from university semester examinations. Contact your HOD immediately."

        return f"Hi {student['name']}, your current attendance is {att}% ({status}).\n\n📋 College Rubrics & Action Required:\n{advice}\n\n💡 Ask 'Can I bunk?' to calculate your safe attendance margin!"

    # Fees
    if any(k in msg for k in ["fee", "fees", "dues", "balance", "pending", "shulk", "shulka"]) and any(k in msg for k in ["my", "how", "what", "check", "kiti"]):
        due = student["fees_due"]
        if due and due > 0:
            return f"Hi {student['name']}, you have Rs {due:.0f} in pending fees. You can pay online via the student ERP portal or at Accounts Counter 4."
        return f"Hi {student['name']}, you have no pending fees. You're completely all clear! 🎉"

    # Exams
    if ("exam" in msg or "exams" in msg or "datesheet" in msg or "timetable" in msg or "pariksha" in msg) and ("my" in msg or "meri" in msg or "majhi" in msg):
        return f"Hi {student['name']}, your next semester examination begins on {student['exam_date']}. Admit cards are downloadable from the student portal."

    # CGPA / Marks / Results
    if any(k in msg for k in ["cgpa", "sgpa", "gpa", "marks", "result", "grade", "score", "gun"]) and any(k in msg for k in ["my", "what", "how", "majhe"]):
        return f"Hi {student['name']}, your current CGPA is {student['cgpa']} / 10.0 in {student['course']} ({student['semester']}). Keep up the great work! 🌟"

    # Mentor / Guide
    if any(k in msg for k in ["mentor", "guide", "counselor", "class teacher"]) and any(k in msg for k in ["my", "who"]):
        return f"Hi {student['name']}, your designated faculty mentor is {student['mentor']}. You can contact them during mentoring hours or via email."

    # Course / Semester
    if any(k in msg for k in ["course", "semester", "branch", "program"]) and any(k in msg for k in ["my", "which", "what"]):
        return f"Hi {student['name']}, you are currently registered in {student['course']}, {student['semester']}."

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
    bot_response = None
    category = None
    source = "Knowledge Base"

    # Check personalized queries first if student is logged in
    if roll_no:
        bot_response = personalized_answer(user_message, roll_no)
        if bot_response:
            category = "Personalized Portal"
            source = "Student Database"

    if not bot_response:
        bot_response, category = match_query(user_message)
        
        # If knowledge base returned fallback (low confidence), try Gemini AI Hybrid
        if not category:
            gemini_ans = ask_gemini(user_message)
            if gemini_ans:
                bot_response = f"{gemini_ans}\n\n*(🤖 Verified Campus AI Hybrid)*"
                category = "Campus AI (Gemini)"
                source = "Gemini Hybrid"

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
