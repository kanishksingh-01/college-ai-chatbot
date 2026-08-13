"""
app.py
Flask backend for the AI Chatbot for College project.
Run: python app.py   (make sure you've run database.py first)
"""

import sqlite3
from flask import Flask, request, jsonify, session, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-submission"  # used for session/login
DB_NAME = "college_chatbot.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- CHATBOT LOGIC (rule-based keyword matching) ----------------

def match_query(message):
    """
    Very simple rule-based NLP: lowercase the message, then check it against
    each category's keyword list. Returns the first matching answer, or a
    fallback message if nothing matches.
    """
    message = message.lower()
    conn = get_db()
    rows = conn.execute("SELECT category, keywords, answer FROM college_info").fetchall()
    conn.close()

    for row in rows:
        keywords = [k.strip() for k in row["keywords"].split(",")]
        for kw in keywords:
            if kw in message:
                return row["answer"], row["category"]

    return (
        "Sorry, I couldn't understand that. You can ask me about admission, "
        "fees, exam timetable, attendance, library timings, courses, or faculty "
        "contacts.",
        None,
    )


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
    return render_template("index.html", student_name=session.get("student_name"))


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

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

    return jsonify({"response": bot_response})


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
            error = "Roll number not found. Please check and try again."

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
            "SELECT * FROM admin WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()

        if admin:
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


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
