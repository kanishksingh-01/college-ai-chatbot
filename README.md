# AI Chatbot for College (GH Raisoni College)

2nd Year BBA CA Project — Kanishk Singh (ISTU25010120001) & Vibhor Saini (ISTU25010120002)

Live Deployment: [https://college-ai-chatbot-c94w.onrender.com](https://college-ai-chatbot-c94w.onrender.com)

---

## 🌟 Key Features & Highlights

- **Modern Glassmorphic UI**: High-end responsive design with Google *Plus Jakarta Sans*, sleek message bubbles, and college branding.
- **Dark Mode & Light Mode**: Seamless theme switching with persistent local storage.
- **Voice Input (Speech-to-Text)**: Speak queries aloud via the browser Web Speech API (Chrome / Safari).
- **Text-to-Speech (Read Aloud)**: High-quality audio readout of bot responses with a single click.
- **Interactive Audio Effects**: Synthesized Web Audio sound effects on message send and receive (with mute toggle).
- **Expanded Knowledge Base (14 Categories)**:
  - Admissions & Eligibility
  - Fee Structure (per annum breakdown table)
  - Exam Timetable & Admit Cards
  - Attendance Rules & Medical Condonation
  - Training & Placements (recruiter packages & internship details)
  - Hostel & Mess Facilities (fees & curfew rules)
  - Scholarships & Government Schemes (MahaDBT & NSP)
  - Library Timings & E-Resources
  - Course Information & Syllabus
  - Key Faculty & HOD Directory
  - Branch Change / Transfer Policy
  - Clubs, Cultural Fests & Sports
  - Campus Emergency & Anti-Ragging Helpline
  - Campus Map, Directions & Metro Transit
- **Personalized Student Self-Service Portal**:
  - Full Student Profile Summary (`"my profile"`, `"who am i"`)
  - Real-time Lecture Attendance (`"what is my attendance?"`)
  - Pending Fee Balance (`"how much are my fees?"`)
  - Cumulative GPA / CGPA (`"what is my CGPA?"`)
  - Designated Faculty Mentor (`"who is my mentor?"`)
  - Upcoming Semester Exam Date (`"when is my exam?"`)
- **Interactive Message Controls**:
  - One-click copy with toast notifications
  - Student feedback collection (👍 Helpful / 👎 Needs Improvement)
  - Export entire chat transcript as a `.txt` file
  - Clear conversation and session reset
- **Upgraded Admin Command Center**:
  - KPI Metrics (Total FAQs, Queries Handled, Registered Students)
  - Real-time Search & Filter for FAQs and Chat Logs
  - One-click CSV Export of Student Query Logs for academic reporting
  - CRUD operations on Knowledge Base entries
  - Securely hashed password management (PBKDF2/scrypt)
- **Progressive Web App (PWA)**: Installable on Android, iOS, Windows, and macOS with service worker caching.

---

## 🚀 How to Run Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```bash
   python database.py
   ```

3. **Start the Application**:
   ```bash
   python app.py
   ```

4. **Access in Browser**:
   - Chatbot: [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - Student Login: [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)
   - Admin Command Center: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

---

## 🔑 Demo Logins

### Student Login ([/login](http://127.0.0.1:5000/login))
Try asking personalized questions after logging in:
- `ISTU00000001`: Aarav Sharma (86.5% Attendance, 8.92 CGPA, No fees pending)
- `ISTU00000002`: Priya Patel (78.0% Attendance, 7.84 CGPA, Rs 5,000 pending)
- `ISTU00000003`: Rohan Kulkarni (67.5% Attendance - Shortage Alert, Rs 12,000 pending)
- `ISTU00000004`: Sneha Deshmukh (94.0% Attendance, 9.45 CGPA, All Clear)

### Admin Login ([/admin](http://127.0.0.1:5000/admin))
- **Username**: `admin`
- **Password**: `admin123`

---

## 📊 Database Schema

- **`college_info`**: `id`, `category`, `keywords`, `answer`
- **`students`**: `roll_no`, `name`, `attendance`, `fees_due`, `exam_date`, `course`, `semester`, `cgpa`, `mentor`
- **`chat_history`**: `id`, `roll_no`, `user_query`, `bot_response`, `timestamp`, `feedback`
- **`admin`**: `username`, `password_hash`
