"""
app.py
Flask backend for the AI Chatbot for College project.
Run: python app.py   (make sure you've run database.py first)
"""

import os
import re
import sqlite3
import difflib
from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

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
    Rule-based NLP with light fuzzy matching:
    1. Exact substring match against each category's keyword list (strongest signal).
    2. If nothing matches exactly, try close-match (typo tolerant) comparison against
       individual words in the message, using difflib's sequence matching.
    Returns (answer, category) or a fallback message if nothing matches well enough.
    """
    message_lower = message.lower()
    words = re.findall(r"[a-zA-Z]+", message_lower)

    conn = get_db()
    rows = conn.execute("SELECT category, keywords, answer FROM college_info").fetchall()
    conn.close()

    best_row = None
    best_score = 0

    for row in rows:
        keywords = [k.strip() for k in row["keywords"].split(",")]
        score = 0
        for kw in keywords:
            if kw in message_lower:
                score += 2  # exact substring match is a strong signal
            else:
                close = difflib.get_close_matches(kw, words, n=1, cutoff=0.82)
                if close:
                    score += 1  # fuzzy/typo-tolerant match is a weaker signal
        if score > best_score:
            best_score = score
            best_row = row

    if best_row:
        return best_row["answer"], best_row["category"]

    return (
        "Sorry, I couldn't understand that. You can ask me about admission, "
        "fees, exam timetable, attendance, library timings, courses, or faculty "
        "contacts \u2014 or tap one of the buttons above.",
        None,
    )


def get_categories():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT category FROM college_info ORDER BY id").fetchall()
    conn.close()
    return [r["category"] for r in rows]


def personalized_answer(message, roll_no):
    """
    If a logged-in student asks about 'my attendance' / 'my fees' / 'my exam',
    fetch their specific record instead of the generic FAQ answer.
    """
    message = message.lower()
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
    ).fetchone()
    conn.close()

    if not student:
        return None

    if "my" in message and "attendance" in message:
        return f"Hi {student['name']}, your current attendance is {student['attendance']}%."
    if "my" in message and ("fee" in message or "fees" in message):
        due = student["fees_due"]
        if due and due > 0:
            return f"Hi {student['name']}, you have Rs {due:.0f} in pending fees."
        return f"Hi {student['name']}, you have no pending fees. You're all clear!"
    if "my" in message and "exam" in message:
        return f"Hi {student['name']}, your next exam date is {student['exam_date']}."

    return None


# ---------------- ROUTES: CHAT UI ----------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        student_name=session.get("student_name"),
        categories=get_categories(),
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"response": "Please type a question."})

    roll_no = session.get("roll_no")
    bot_response = None

    # check personalized queries first if student is logged in
    if roll_no:
        bot_response = personalized_answer(user_message, roll_no)

    category = None
    if not bot_response:
        bot_response, category = match_query(user_message)

    # save to chat history
    conn = get_db()
    conn.execute(
        "INSERT INTO chat_history (roll_no, user_query, bot_response) VALUES (?, ?, ?)",
        (roll_no, user_message, bot_response),
    )
    conn.commit()
    conn.close()

    return jsonify({"response": bot_response, "category": category})


# ---------------- ROUTES: STUDENT LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        roll_no = request.form.get("roll_no", "").strip()
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
    faqs = conn.execute("SELECT * FROM college_info").fetchall()
    history = conn.execute(
        "SELECT * FROM chat_history ORDER BY id DESC LIMIT 50"
    ).fetchall()
    conn.close()

    return render_template("admin_dashboard.html", faqs=faqs, history=history)


@app.route("/admin/add", methods=["POST"])
def admin_add():
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    category = request.form.get("category")
    keywords = request.form.get("keywords")
    answer = request.form.get("answer")

    conn = get_db()
    conn.execute(
        "INSERT INTO college_info (category, keywords, answer) VALUES (?, ?, ?)",
        (category, keywords, answer),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete/<int:faq_id>")
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
