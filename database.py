"""
database.py
Creates and seeds the SQLite database for the AI Chatbot for College project.
Run this once (python database.py) before starting app.py.
"""

import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "college_chatbot.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # ---------- TABLES ----------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS college_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        keywords TEXT NOT NULL,
        answer TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        roll_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        attendance REAL,
        fees_due REAL,
        exam_date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        user_query TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL
    )
    """)

    # ---------- SEED DATA (placeholder — edit freely) ----------

    cur.execute("SELECT COUNT(*) FROM college_info")
    if cur.fetchone()[0] == 0:
        college_info_data = [
            (
                "Admission",
                "admission,admissions,apply,enrollment,enroll,eligibility",
                "Admissions for the new academic year are open from June to August. "
                "Eligibility: 10+2 pass with minimum 45% marks. Apply online at "
                "college.edu/admissions or visit the admission office (Room 101)."
            ),
            (
                "Fee Structure",
                "fee,fees,fee structure,payment,tuition",
                "FEE STRUCTURE (per year):\n"
                "| Course | Tuition Fee | Exam Fee | Total |\n"
                "|--------|-------------|----------|-------|\n"
                "| BBA CA | Rs 45,000   | Rs 2,000 | Rs 47,000 |\n"
                "| BCA    | Rs 50,000   | Rs 2,500 | Rs 52,500 |\n"
                "| BCom   | Rs 35,000   | Rs 1,500 | Rs 36,500 |\n"
                "Fees can be paid online via the student portal or at the accounts office."
            ),
            (
                "Exam Timetable",
                "exam,exams,timetable,time table,schedule,datesheet",
                "Exam timetable will be displayed by the college as soon as exams are "
                "announced. It is given by the class teacher as well as the Head of "
                "Department (HOD) as per the academic calendar of the semester.\n\n"
                "EXAM TIMETABLE (Semester III):\n"
                "| Date       | Subject              | Time            |\n"
                "|------------|----------------------|-----------------|\n"
                "| 10-Dec-2026 | Business Statistics | 10:00 - 1:00 PM |\n"
                "| 12-Dec-2026 | Computer Applications| 10:00 - 1:00 PM |\n"
                "| 14-Dec-2026 | Financial Accounting | 10:00 - 1:00 PM |\n"
                "| 16-Dec-2026 | Business Communication| 10:00 - 1:00 PM |\n"
                "Admit cards will be available on the student portal one week before exams."
            ),
            (
                "Attendance Rules",
                "attendance,present,absent,shortage",
                "A minimum of 75% attendance is mandatory in each subject to be eligible "
                "to sit for exams. Students with attendance between 65-75% may apply for "
                "condonation with a valid medical certificate. Below 65% attendance results "
                "in detention from exams."
            ),
            (
                "Library Timings",
                "library,books,library timing,library hours",
                "The college library is open Monday to Saturday, 9:00 AM to 6:00 PM. "
                "Closed on Sundays and public holidays. Students can issue up to 3 books "
                "for 14 days using their student ID card."
            ),
            (
                "Course Information",
                "course,courses,syllabus,subjects,program",
                "The college offers BBA (Computer Applications), BCA, and BCom programs, "
                "each 3 years / 6 semesters. Detailed syllabus for each course is available "
                "on the college website under Academics > Syllabus."
            ),
            (
                "Faculty Contact",
                "faculty,professor,teacher,contact,hod,staff",
                "FACULTY CONTACTS:\n"
                "| Department | Faculty Name    | Email                  |\n"
                "|------------|-----------------|-------------------------|\n"
                "| BBA CA HOD | Dr. A. Sharma   | a.sharma@college.edu    |\n"
                "| Computer Apps | Prof. R. Verma | r.verma@college.edu  |\n"
                "| Accounts   | Prof. S. Iyer   | s.iyer@college.edu     |\n"
                "For general queries, email info@college.edu or call the office at 020-1234567."
            ),
            (
                "Branch Change",
                "change branch,change my branch,switch branch,transfer branch,branch change,"
                "change course,change my course,switch course",
                "If you want to change your branch, first contact your HOD. Once the HOD "
                "approves, go to the college principal/director, who will provide further "
                "details.\n"
                "Note: If you change your course or branch, the fee structure may vary. If "
                "the new fee is higher than your current one, you will need to pay the "
                "difference. If the new fee is lower, the difference will be refunded."
            ),
        ]
        cur.executemany(
            "INSERT INTO college_info (category, keywords, answer) VALUES (?, ?, ?)",
            college_info_data
        )

    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        students_data = [
            ("ISTU00000001", "Demo Student A", 82.5, 0, "10-Dec-2026"),
            ("ISTU00000002", "Demo Student B", 78.0, 5000, "10-Dec-2026"),
            ("ISTU00000003", "Demo Student C", 68.0, 12000, "10-Dec-2026"),
        ]
        cur.executemany(
            "INSERT INTO students (roll_no, name, attendance, fees_due, exam_date) VALUES (?, ?, ?, ?, ?)",
            students_data
        )

    cur.execute("SELECT COUNT(*) FROM admin")
    if cur.fetchone()[0] == 0:
        # Default admin login: admin / admin123 — change this before final submission!
        cur.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123"))
        )
    conn.commit()
    conn.close()
    print("Database initialized: college_chatbot.db")


if __name__ == "__main__":
    init_db()
