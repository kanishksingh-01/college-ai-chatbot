# AI Chatbot for College

2nd Year BBA CA Project — Kanishk Singh (ISTU25010120001) & Vibhor Saini (ISTU25010120002)

## How to run

1. Install Flask (only dependency needed):
   ```
   pip install flask
   ```

2. Initialize the database (creates college_chatbot.db with placeholder data):
   ```
   python database.py
   ```

3. Start the app:
   ```
   python app.py
   ```

4. Open your browser to: http://127.0.0.1:5000

## What's new in this version

- Fuzzy/typo-tolerant matching (e.g. "libary timmings" still matches Library Timings)
- Quick-reply category buttons under the welcome message
- Typing indicator animation before bot responses
- College-branded header and polished, mobile-responsive UI
- Admin passwords are now securely hashed (not stored in plain text)
- Admin can change their password from the dashboard
- Reads PORT and SECRET_KEY from environment variables (Render-ready)

## Logins for demo

**Student login** (try personalized questions like "what is my attendance" or "how much are my fees" after logging in):
- Roll No: ISTU25010120001 (Kanishk Singh — no pending fees)
- Roll No: ISTU25010120002 (Vibhor Saini — Rs 5000 pending fees)
- Roll No: ISTU25010120099 (Sample Student)

**Admin login** (http://127.0.0.1:5000/admin):
- Username: admin
- Password: admin123
- ⚠️ Change this password in database.py before final submission.

## What the chatbot can answer (no login needed)

Ask about: admission, fee structure, exam timetable, attendance rules,
library timings, course information, faculty contacts.

## Editing placeholder data

All FAQ answers and student records are placeholder/sample data. To edit:
- Easiest: log in as admin and use the dashboard to add/delete FAQs.
- Or edit the `college_info_data` and `students_data` lists directly in
  `database.py`, delete `college_chatbot.db`, and re-run `python database.py`
  to reseed with your real college data.

## Project structure

```
chatbot/
├── app.py                 # Flask backend + chatbot logic + routes
├── database.py             # Creates & seeds the SQLite database
├── requirements.txt
├── templates/
│   ├── index.html          # Main chat interface
│   ├── login.html          # Student login
│   ├── admin_login.html    # Admin login
│   └── admin_dashboard.html # Admin panel (FAQ management + chat history)
└── static/
    ├── style.css
    └── script.js
```

## Database schema

- **college_info**: id, category, keywords, answer — the FAQ knowledge base
- **students**: roll_no, name, attendance, fees_due, exam_date
- **chat_history**: id, roll_no, user_query, bot_response, timestamp
- **admin**: username, password

Use this schema directly for your project report's ER Diagram and SQL tables section.
