"""
app.py
Flask backend for the AI Chatbot for College project.
GH Raisoni College - BBA Computer Applications
"""

import os
import re
import csv
import io
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


# ---------------- CHATBOT LOGIC (rule-based keyword matching with fuzzy fallback) ----------------

def match_query(message):
    """
    Rule-based NLP with typo tolerance:
    1. Exact substring match against each category's keyword list.
    2. Fuzzy match against individual words in the message using difflib.
    Returns (answer, category) or a fallback message if nothing matches.
    """
    message_lower = message.lower()
    words = re.findall(r"[a-zA-Z0-9]+", message_lower)

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
        "Scholarships, or Faculty Contacts — or tap one of the suggested topics below.",
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
            f"• Next Exam Date: {student['exam_date']}"
        )

    # Attendance
    if "attendance" in msg and any(k in msg for k in ["my", "what", "how", "current", "show"]):
        status = "Good standing (eligible for exams)" if student["attendance"] >= 75 else "⚠️ Shortage alert (<75% threshold)"
        return f"Hi {student['name']}, your current attendance is {student['attendance']}% ({status})."

    # Fees
    if any(k in msg for k in ["fee", "fees", "dues", "balance", "pending"]) and any(k in msg for k in ["my", "how", "what", "check"]):
        due = student["fees_due"]
        if due and due > 0:
            return f"Hi {student['name']}, you have Rs {due:.0f} in pending fees. You can pay online via the student ERP portal or at Accounts Counter 4."
        return f"Hi {student['name']}, you have no pending fees. You're completely all clear! 🎉"

    # Exams
    if ("exam" in msg or "exams" in msg or "datesheet" in msg or "timetable" in msg) and "my" in msg:
        return f"Hi {student['name']}, your next semester examination begins on {student['exam_date']}. Admit cards are downloadable from the student portal."

    # CGPA / Marks / Results
    if any(k in msg for k in ["cgpa", "sgpa", "gpa", "marks", "result", "grade", "score"]) and any(k in msg for k in ["my", "what", "how"]):
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

    # Check personalized queries first if student is logged in
    if roll_no:
        bot_response = personalized_answer(user_message, roll_no)

    category = None
    if not bot_response:
        bot_response, category = match_query(user_message)

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
        "history_id": history_id
    })


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
    conn.close()

    return render_template(
        "admin_dashboard.html",
        faqs=faqs,
        history=history,
        total_faqs=len(faqs),
        total_chats=total_chats,
        total_students=total_students,
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
