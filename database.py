"""
database.py
Creates and seeds the SQLite database for the AI Chatbot for College project.
Run this (python database.py) to initialize or update the database.
"""

import sqlite3

try:
    from werkzeug.security import generate_password_hash
except ImportError:
    import hashlib
    def generate_password_hash(password):
        salt = "7x4k8m9q2w1e6r3t"
        h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000).hex()
        return f"pbkdf2:sha256:600000${salt}${h}"

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
        exam_date TEXT,
        course TEXT,
        semester TEXT,
        cgpa REAL,
        mentor TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        user_query TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        feedback TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL
    )
    """)

    # Check and migrate columns if upgrading from earlier version
    cur.execute("PRAGMA table_info(students)")
    student_cols = [c[1] for c in cur.fetchall()]
    for col, col_type in [
        ("course", "TEXT"),
        ("semester", "TEXT"),
        ("cgpa", "REAL"),
        ("mentor", "TEXT"),
    ]:
        if col not in student_cols:
            cur.execute(f"ALTER TABLE students ADD COLUMN {col} {col_type}")

    cur.execute("PRAGMA table_info(chat_history)")
    chat_cols = [c[1] for c in cur.fetchall()]
    if "feedback" not in chat_cols:
        cur.execute("ALTER TABLE chat_history ADD COLUMN feedback TEXT")

    # ---------- SEED DATA ----------

    college_info_data = [
        (
            "Admission",
            "admission,admissions,apply,enrollment,enroll,eligibility,entrance,how to apply,registration process,pravesh,dakhila,admission kaise le,pravesh prakriya,pravesh niyam,admission kab shuru",
            "🎓 ADMISSIONS (Academic Year 2026-27):\n"
            "• Application Period: June 1 to August 15.\n"
            "• Eligibility: 10+2 (Higher Secondary) with minimum 45% aggregate (40% for reserved categories).\n"
            "• Selection: Based on merit & academic counseling.\n"
            "• How to apply: Submit online at admissions.ghrc.edu or visit the Central Admission Office (Admin Block, Room 101).\n"
            "• Helpline: +91 712-6617100 / admissions@college.edu"
        ),
        (
            "Fee Structure",
            "fee,fees,fee structure,payment,tuition,cost,dues,installment,shulk,shulka,kiti fee,fee kiti ahe,kitni fees,fees kitni,paisa,kharch",
            "💰 FEE STRUCTURE (Academic Year 2026-27 per annum):\n\n"
            "| Course | Tuition Fee | Exam & Lab Fee | Total Annual Fee |\n"
            "|--------|-------------|----------------|------------------|\n"
            "| BBA CA | Rs 45,000   | Rs 2,000       | Rs 47,000        |\n"
            "| BCA    | Rs 50,000   | Rs 2,500       | Rs 52,500        |\n"
            "| BCom   | Rs 35,000   | Rs 1,500       | Rs 36,500        |\n"
            "| MCA    | Rs 65,000   | Rs 3,000       | Rs 68,000        |\n\n"
            "• Payment Modes: Online via ERP Student Portal, UPI, Net Banking, or Demand Draft at Accounts Section (Counter 4).\n"
            "• Installments: Available upon special approval from the Finance Dean."
        ),
        (
            "Exam Timetable",
            "exam,exams,timetable,time table,schedule,datesheet,admit card,hall ticket,semester exam,pariksha,pariksha kadhi,exam kab hai,paper schedule",
            "📅 UPCOMING SEMESTER EXAMINATIONS:\n\n"
            "EXAM SCHEDULE (Semester III):\n"
            "| Date        | Subject                | Shift / Timing  |\n"
            "|-------------|------------------------|-----------------|\n"
            "| 10-Dec-2026 | Business Statistics    | 10:00 - 1:00 PM |\n"
            "| 12-Dec-2026 | Computer Applications  | 10:00 - 1:00 PM |\n"
            "| 14-Dec-2026 | Financial Accounting   | 10:00 - 1:00 PM |\n"
            "| 16-Dec-2026 | Business Communication | 10:00 - 1:00 PM |\n"
            "| 18-Dec-2026 | RDBMS & SQL Lab Exam   | 09:30 - 12:30 PM|\n\n"
            "📌 Note: Admit cards / Hall tickets will be issued through the ERP portal exactly 7 days before commencement. Carrying your Student ID card is strictly mandatory."
        ),
        (
            "Attendance Rules",
            "attendance,present,absent,shortage,minimum attendance,criteria,medical leave,detention,detention policy,rubrics,hajeri,hazari,upasthiti,attendance niyam",
            "📊 ATTENDANCE REGULATIONS & OFFICIAL DETENTION POLICY (PUNE CAMPUS):\n\n"
            "• Mandatory Requirement: Minimum 75% overall attendance is mandatory to appear for university end-semester examinations.\n\n"
            "📋 OFFICIAL DETENTION RUBRICS (Implementation of Student Detention Policy):\n"
            "1. Above 75% (Good Standing):\n"
            "   - Status: Fully eligible to appear for semester examinations.\n\n"
            "2. 60% to 75% Attendance (Excluding Medical):\n"
            "   - Theory Rubric: End Sem Examination Paper Sets of previous 2 years to be solved in Open Book mode in the College.\n"
            "   - Practical Rubric: Student will not be eligible for the attendance mark component of internal marks.\n\n"
            "3. 50% to 59.99% Attendance (Excluding Medical):\n"
            "   - Theory Rubric: (1) End Sem Examination Paper Sets of previous 2 years to be solved in Open Book mode in the College. (2) Student must appear for a prelim examination and score a minimum of 60% marks to be eligible to get out of detention.\n"
            "   - Practical Rubric: Student must appear for a practical-based prelim examination and score a minimum of 60% marks to get out of detention (Max 2 practicals conducted in a day).\n\n"
            "4. Below 50% Attendance (<50%):\n"
            "   - Theory & Practical: No consideration. Strictly detained from semester examinations.\n\n"
            "📌 Tip: Logged-in students can view real-time percentage and specific detention rubrics by asking 'what is my attendance?'."
        ),
        (
            "Library Timings",
            "library,books,library timing,library hours,digital library,reading room,borrow,granthalay,pustak,kitabe,reading hall",
            "📚 CENTRAL KNOWLEDGE RESOURCE CENTRE (LIBRARY):\n"
            "• Monday to Saturday: 8:30 AM – 7:00 PM\n"
            "• Reading Hall: Open 24/7 during preparatory leave and examination weeks.\n"
            "• Sundays & Holidays: Closed.\n"
            "• Borrowing Limits: UG students can issue 3 books for 14 days; PG students can issue 5 books.\n"
            "• E-Resources: Access IEEE Xplore, DELNET, and NDL free with campus Wi-Fi."
        ),
        (
            "Course Information",
            "course,courses,syllabus,subjects,program,curriculum,degree,specialization,abhyaskram,vishay,shikshan",
            "📖 ACADEMIC PROGRAMS & COURSES OFFERED:\n"
            "• BBA (Computer Applications): 3 Years / 6 Semesters — Blends management with modern software dev, Cloud, and Data Analytics.\n"
            "• BCA (Bachelor of Computer Applications): 3 Years — Focuses on AI/ML, Full-Stack Web, Cyber Security.\n"
            "• B.Com (Computer Applications / Finance): 3 Years — Commerce, Auditing, Fintech, GST.\n"
            "• MCA (Master of Computer Applications): 2 Years — Advanced Software Engineering, Cloud Architecture.\n"
            "Detailed syllabus PDFs are downloadable from the college portal under Academics > Syllabus."
        ),
        (
            "Faculty Contact",
            "faculty,professor,teacher,contact,hod,staff,email,directory,head of department,shikshak,pradhyapak,teachers list",
            "👨‍🏫 KEY FACULTY & DEPARTMENT CONTACTS:\n\n"
            "| Role / Department     | Faculty Name    | Email ID                 |\n"
            "|-----------------------|-----------------|--------------------------|\n"
            "| Head of Dept (BBA CA) | Dr. A. Sharma   | a.sharma@college.edu     |\n"
            "| Assistant Professor   | Prof. R. Verma  | r.verma@college.edu      |\n"
            "| Accounts Officer      | Prof. S. Iyer   | s.iyer@college.edu       |\n"
            "| Training & Placement  | Dr. N. Patil    | placements@college.edu   |\n"
            "| Examination In-Charge | Prof. K. Deshmukh| exams@college.edu       |\n\n"
            "For general queries, contact helpdesk@college.edu or dial Ext. 102."
        ),
        (
            "Branch Change",
            "change branch,change my branch,switch branch,transfer branch,branch change,change course,change my course,switch course,branch badalne,branch badalna",
            "🔄 BRANCH / COURSE TRANSFER POLICY:\n"
            "1. Eligibility: Branch change requests are accepted only at the start of Semester II or III, subject to seat vacancy and minimum 7.5 CGPA in Year 1.\n"
            "2. Approval Process: Submit the transfer form countersigned by your existing HOD and the destination HOD to the Principal's Office.\n"
            "3. Fee Adjustment: If the new course tuition is higher, the student must deposit the difference. If lower, excess fees are adjusted against next semester dues."
        ),
        (
            "Placements",
            "placement,placements,job,jobs,package,recruiter,recruiters,internship,internships,career,salary,highest package,naukri,rojgar,nokari",
            "💼 TRAINING & PLACEMENT CELL (T&P):\n"
            "• Placement Rate: 92%+ eligible students placed in 2025-26.\n"
            "• Highest Package: Rs 14.5 LPA | Average Package: Rs 4.8 LPA.\n"
            "• Top Recruiters: TCS, Infosys, Wipro, Capgemini, Accenture, Cognizant, Tech Mahindra, ICICI Bank.\n"
            "• Internship Drives: Commences in 5th Semester with stipend opportunities from Rs 15,000 to Rs 35,000/month.\n"
            "• Contact: T&P Office, Ground Floor, Placement Block | placements@college.edu"
        ),
        (
            "Hostel & Mess",
            "hostel,hostels,accommodation,room,stay,hostel fee,warden,curfew,vasatigruh,vasatigruh fee,rehne ki jagah,kamra",
            "🏢 HOSTEL & RESIDENTIAL FACILITIES:\n"
            "• Accommodation: Separate air-conditioned and non-AC hostels for boys and girls with 24/7 security & CCTV.\n"
            "• Amenities: Wi-Fi, laundry facilities, study lounges, gym, indoor sports room.\n"
            "• Fees: Rs 65,000 to Rs 85,000/year (including food & accommodation).\n"
            "• Curfew / In-Time: 8:30 PM sharp. Overnight gate passes require parent SMS verification."
        ),
        (
            "Scholarships",
            "scholarship,scholarships,financial aid,freeship,concession,mahadbt,nsp,fee waiver,shishyavrutti,chatravritti",
            "🏅 SCHOLARSHIPS & FINANCIAL ASSISTANCE:\n"
            "1. Merit Scholarship: 25% to 50% tuition waiver for students scoring >85% in 12th board exams or university rankers.\n"
            "2. Government Schemes: Full guidance for MahaDBT, Post-Matric Scholarship (SC/ST/OBC/EBC), and National Scholarship Portal (NSP).\n"
            "3. Sports Quota: Special concessions for national and state-level sports medalists.\n"
            "• Scholarship Desk: Room 104, Admin Wing (Contact Mr. Joshi: scholarships@college.edu)."
        ),
        (
            "Clubs & Extracurriculars",
            "club,clubs,sports,activities,gym,events,fest,cultural,hackathon,nss,ncc,khel,antarang,sanskrutik",
            "🎨 STUDENT CLUBS & EXTRACURRICULARS:\n"
            "• Tech Clubs: Coding Ninjas Chapter, Google Developer Student Club (GDSC), Robotics Club.\n"
            "• Cultural & Arts: Music Club, Dance Troupe, Dramatics Society, Annual Fest 'ANTRANG'.\n"
            "• Sports & Fitness: Cricket pitch, basketball courts, badminton arena, Olympic gymnasium.\n"
            "• Social Service: Active NSS & NCC units for community service and leadership development."
        ),
        (
            "Emergency & Helpline",
            "emergency,helpline,ragging,anti ragging,complaint,grievance,doctor,medical,clinic,security,madat,tatkal,suraksha",
            "🚨 CAMPUS EMERGENCY & STUDENT HELPLINE (PUNE CAMPUS):\n"
            "• Campus Security / Gate Control: +91 20-67528000 / +91 9604787185 (24/7)\n"
            "• Anti-Ragging Helpline (Zero Tolerance): 1800-180-5522 | antiragging@college.edu\n"
            "• Women Grievance / ICC Cell: icc.pune@raisoni.net\n"
            "• Health Care Center / First Aid: Medical Unit, Ground Floor near Sports Complex (Full-time doctor on campus).\n"
            "• Student Counselor: counselor.pune@raisoni.net (Confidential mental health & career counseling)."
        ),
        (
            "Campus Location & Map",
            "location,address,where is campus,map,campus,how to reach,bus,transport,nearest metro,pune,wagholi,yerwada,yerawada,campuses,airport road,shastrinagar,domkhel,kahan hai,kothe ahe,patta",
            "📍 GH RAISONI COLLEGE PUNE — CAMPUS ADDRESSES & CONNECTIVITY:\n\n"
            "🏛️ 1. WAGHOLI CAMPUS (Main Academic Campus):\n"
            "• Address: Gat 1200, Domkhel Rd, Wagholi, Pune, Maharashtra 412207.\n"
            "• Programs Offered: BBA-CA, BCA, B.Com (Computer Applications), MCA & Engineering.\n"
            "• Connectivity: Off Pune-Ahmednagar State Highway. College buses connect major routes across Pune (Kharadi, Hadapsar, Viman Nagar, Pune Station, Shivaji Nagar).\n"
            "• Nearest Railway Station: Pune Junction Railway Station (~14 km).\n"
            "• Nearest Airport: Pune International Airport, Lohegaon (~10 km).\n\n"
            "🏢 2. YERAWADA CAMPUS (City Campus):\n"
            "• Address: Nyati Unitree East-Wing, Deepak Fertilizer Building, Airport Rd, Shastrinagar, Yerawada, Pune, Maharashtra 411006.\n"
            "• Landmark: Near Shastrinagar Chowk, Airport Road, Yerawada.\n"
            "• Connectivity: Strategically located on Airport Road, ~3.5 km from Pune Airport and ~5.5 km from Pune Junction.\n\n"
            "🌐 Official Portal: pune.raisoni.net | Affiliated to Savitribai Phule Pune University (SPPU)"
        ),
        (
            "Canteen & Mess Menu",
            "canteen,mess,mess menu,food,food menu,canteen menu,mess food,breakfast,lunch,today food,khana,jevan,nashta,thali,canteen rate,snacks,dinner menu",
            "🍛 CAMPUS CANTEEN & MESS SCHEDULE (Daily Fresh Menu):\n\n"
            "| Meal | Timings | Popular Daily Specials | Price |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| ☕ Breakfast | 08:00 AM – 10:00 AM | Poha, Upma, Idli Sambhar, Misal Pav, Tea/Coffee | Rs 30 - 45 |\n"
            "| 🍱 Lunch (Thali) | 12:30 PM – 02:30 PM | Special Student Veg Thali (2 Sabzi, 3 Roti, Dal, Rice, Salad) | Rs 70 |\n"
            "| 🥪 Snacks / High Tea | 04:30 PM – 06:00 PM | Samosa, Vada Pav, Veg Sandwich, Cold Coffee | Rs 20 - 40 |\n"
            "| 🍲 Dinner (Hostel) | 07:30 PM – 09:30 PM | Deluxe Thali / Paneer / Egg Curry, Jeera Rice, Sweet | Rs 80 |\n\n"
            "• Hygiene Certified: FSSAI Grade-A Clean Kitchen & RO Drinking Water.\n"
            "• Canteen In-charge: Mr. Pawar (+91-20-67528120)."
        ),
        (
            "Campus Floor & Room Locator",
            "where is lab,where is accounts,lab 302,accounts counter,room 101,audi,seminar hall,find room,floor guide,campus navigator,lost,lift,elevator,building map,room locator,where is office",
            "🗺️ CAMPUS INDOOR NAVIGATOR & FLOOR DIRECTORY:\n\n"
            "| Facility / Department | Floor / Wing | Directions & Landmarks |\n"
            "| :--- | :--- | :--- |\n"
            "| 🏛️ Central Admissions Office | Ground Floor, Admin Block (Room 101) | Right at main entrance foyer |\n"
            "| 💳 Accounts & Fee Counter 4 | Ground Floor, Admin Block | Next to Admission Office |\n"
            "| 🩺 Medical Room & Dispensary | Ground Floor, Sports Complex | Opposite Olympic Gymnasium |\n"
            "| 📚 Central Library & Reading Hall | 1st Floor, Academic Block A | Take Elevator A, turn right |\n"
            "| 💻 Computer Labs 201 – 204 | 2nd Floor, Skill Tech Block | High-speed Linux & Coding Labs |\n"
            "| 💼 Training & Placement Cell | 2nd Floor, Placement Wing | Next to Seminar Hall 1 |\n"
            "| 🔬 Advanced Project Labs 301–304 | 3rd Floor, Skill Tech Block | BBA-CA / BCA Project Hub |\n"
            "| 🎭 Central Auditorium (Audi 2) | 3rd Floor, Cultural Wing | Main Hall (Capacity 600) |\n\n"
            "💡 Pro-Tip: You can ask specific queries like 'Where is Lab 302?' or 'Where is Counter 4?' anytime."
        ),
        (
            "Bonafide & Document Services",
            "bonafide,noc,certificate,application,document,lor,migration,bus pass,railway concession,identity certificate,bonafide certificate,apply certificate",
            "📄 STUDENT DOCUMENT & BONAFIDE SERVICES:\n\n"
            "• Available Certificates: Bonafide Certificate (MahaDBT / Bus Pass / Bank / Passport), Internship NOC, Transfer Certificate (TC), Migration.\n"
            "• Instant Digital Draft: Logged-in students can type 'generate bonafide certificate' to preview and print an official pre-filled certificate immediately!\n"
            "• Processing Hard Copies: Physical sealed copies are issued within 24–48 hours at Student Section (Admin Counter 2).\n"
            "• Requirements: Previous semester mark sheet copy, fee clearance receipt, and Student ID card."
        ),
        (
            "Attendance & Bunk Calculator Guide",
            "bunk,can i bunk,how many bunk,miss class,skip class,attendance target,bunk calculator,calculate attendance,bunk kitne kar sakte,target attendance",
            "🎯 ATTENDANCE & BUNK TARGET CALCULATOR:\n\n"
            "• Mandatory Requirement: 75% overall attendance as per SPPU & Raisoni detention rubrics.\n"
            "• Personalized Calculation:\n"
            "  - Logged-in students can ask: 'Can I bunk?' or 'How many lectures to reach 75%?' to see their real-time calculated safe bunk threshold or required classes!\n"
            "  - You can also click the 🎯 Bunk Tool in the header to open the interactive calculator."
        )
    ]

    # Cleanly refresh FAQ entries
    cur.execute("DELETE FROM college_info")
    cur.executemany(
        "INSERT INTO college_info (category, keywords, answer) VALUES (?, ?, ?)",
        college_info_data
    )

    # Refresh or seed demo students covering all 4 detention brackets
    students_data = [
        (
            "ISTU00000001",
            "Aarav Sharma",
            86.5,
            0.0,
            "10-Dec-2026",
            "BBA (Computer Applications)",
            "Semester III",
            8.92,
            "Dr. A. Sharma"
        ),
        (
            "ISTU00000002",
            "Priya Patel",
            78.0,
            5000.0,
            "10-Dec-2026",
            "BBA (Computer Applications)",
            "Semester III",
            7.84,
            "Prof. R. Verma"
        ),
        (
            "ISTU00000003",
            "Rohan Kulkarni",
            67.5,
            12000.0,
            "10-Dec-2026",
            "BCA",
            "Semester III",
            6.75,
            "Prof. S. Iyer"
        ),
        (
            "ISTU00000004",
            "Sneha Deshmukh",
            94.0,
            0.0,
            "10-Dec-2026",
            "B.Com (Comp Apps)",
            "Semester V",
            9.45,
            "Dr. N. Patil"
        ),
        (
            "ISTU00000005",
            "Aditya Joshi",
            54.5,
            8000.0,
            "10-Dec-2026",
            "BBA (Computer Applications)",
            "Semester III",
            6.20,
            "Prof. R. Verma"
        ),
        (
            "ISTU00000006",
            "Tanvi Shinde",
            42.0,
            15000.0,
            "10-Dec-2026",
            "BCA",
            "Semester III",
            5.80,
            "Dr. A. Sharma"
        ),
        (
            "ISTU25010120001",
            "Kanishk Singh",
            88.5,
            0.0,
            "10-Dec-2026",
            "BBA (Computer Applications)",
            "Semester III",
            9.40,
            "Dr. A. Sharma"
        ),
        (
            "ISTU25010120002",
            "Vibhor Saini",
            82.0,
            0.0,
            "10-Dec-2026",
            "BBA (Computer Applications)",
            "Semester III",
            8.85,
            "Prof. R. Verma"
        )
    ]

    cur.execute("DELETE FROM students")
    cur.executemany(
        "INSERT INTO students (roll_no, name, attendance, fees_due, exam_date, course, semester, cgpa, mentor) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        students_data
    )

    # Seed default admin if missing
    cur.execute("SELECT COUNT(*) FROM admin")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123"))
        )

    conn.commit()
    conn.close()
    print(f"Database successfully updated and seeded: {DB_NAME}")


if __name__ == "__main__":
    init_db()
