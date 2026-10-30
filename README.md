# AI Chatbot for College (GH Raisoni College)

2nd Year BBA CA Project — Kanishk Singh (ISTU25010120001) & Vibhor Saini (ISTU25010120002)

Live Deployment: [https://college-ai-chatbot-c94w.onrender.com](https://college-ai-chatbot-c94w.onrender.com)

---

## 🌟 Key Features & Highlights

- **🎯 Smart Bunk & Attendance Forecaster**: Computes precise safe bunk allowances or consecutive recovery lectures required to meet the 75% SPPU / Raisoni attendance rule (`"can I bunk?"`, `"how many classes to reach 75%?"`), complete with an interactive simulation tool.
- **🪪 Flippable 3D Digital Student Identity Pass**: Interactive 3D campus ID card with photo avatar, verified status badge, scannable QR verification code, barcode, and flippable reverse side showing designated faculty mentor, terms, and registrar seal.
- **🗣️ Multilingual Experience (English | मराठी | हिंदी)**: Instant one-click language toggle in header with full UI localization and multilingual NLP understanding for Hindi, Marathi, and Hinglish queries.
- **🤖 Hybrid AI Engine (Google Gemini Integration)**: Grounded campus fallback powered by Google Gemini API whenever rule-matching confidence is low, providing natural conversational assistance without hallucinations.
- **📄 Instant Bonafide & NOC Certificate Generator**: Official institutional letterhead draft generator for scholarships (MahaDBT), bus/metro concession passes, bank loans, and internship NOC with one-click print & PDF export.
- **🗺️ Campus Indoor Floor & Room Directory**: Interactive building navigator for finding classrooms, laboratories (e.g. Lab 302), Accounts Counter 4, Library, and Auditoriums.
- **🍛 Daily Canteen & Mess Schedule**: Complete daily meal schedule (Breakfast, Lunch Thali, High Tea, Dinner) with pricing and daily specials.
- **🚨 Campus Emergency SOS Speed-Dial**: One-tap emergency dialer for 24/7 Security Gate, National Anti-Ragging Cell, Women's Safety ICC, and Campus Medical Dispensary.
- **Modern Glassmorphic UI**: High-end responsive design with Google *Plus Jakarta Sans*, sleek message bubbles, and college branding.
- **Dark Mode & Light Mode**: Seamless theme switching with persistent local storage.
- **Voice Input (Speech-to-Text)**: Speak queries aloud via the browser Web Speech API (Chrome / Safari).
- **Text-to-Speech (Read Aloud)**: High-quality audio readout of bot responses with a single click.
- **Interactive Audio Effects**: Synthesized Web Audio sound effects on message send, receive, and 3D card flips (with mute toggle).
- **Expanded Knowledge Base (18 Categories)**:
  - Admissions & Eligibility
  - Fee Structure (per annum breakdown table)
  - Exam Timetable & Admit Cards
  - Attendance Rules & Official 4-tier Detention Policy
  - Training & Placements (recruiter packages & internship details)
  - Hostel & Residential Facilities
  - Scholarships & Government Schemes (MahaDBT & NSP)
  - Central Library Timings & E-Resources
  - Course Information & Syllabus
  - Key Faculty & HOD Directory
  - Branch Change / Transfer Policy
  - Clubs, Cultural Fests (ANTRANG) & Sports
  - Campus Emergency & Anti-Ragging Helpline
  - Campus Locations (Wagholi Main & Yerawada City) & Directions
  - Canteen & Mess Daily Menu & Timings
  - Campus Floor & Room Locator
  - Bonafide & Document Services
  - Attendance & Bunk Calculator Guide
- **Personalized Student Self-Service Portal**:
  - Full Student Profile Summary (`"my profile"`, `"who am i"`)
  - Safe Bunk Calculation (`"can I bunk?"`, `"how many classes can I miss?"`)
  - Real-time Lecture Attendance (`"what is my attendance?"`)
  - Digital ID Card Pass (`"show my id card"`)
  - Printable Bonafide Letter (`"generate bonafide certificate"`)
  - Pending Fee Balance (`"how much are my fees?"`)
  - Cumulative GPA / CGPA (`"what is my CGPA?"`)
  - Designated Faculty Mentor (`"who is my mentor?"`)
  - Upcoming Semester Exam Date (`"when is my exam?"`)
- **Upgraded Admin Command Center**:
  - KPI Metrics (Total FAQs, Queries Handled, Registered Students, Gemini AI Status)
  - Unanswered Query Discovery (Missing FAQs Queue) for continuous knowledge improvement
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
