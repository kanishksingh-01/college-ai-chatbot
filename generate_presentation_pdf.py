import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages after page 1)
        if self._pageNumber > 1:
            self.drawString(54, A4[1] - 36, "GH RAISONI COLLEGE AI CAMPUS ASSISTANT — PROJECT PRESENTATION PLAYBOOK")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, A4[1] - 42, A4[0] - 54, A4[1] - 42)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, A4[0] - 54, 46)
        
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Team: Kanishk Singh (Backend) & Vibhor Saini (Frontend) • Live: college-ai-chatbot-c94w.onrender.com")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 54, 32, page_str)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#4A154B")   # Raisoni Plum/Purple
    c_blue = colors.HexColor("#1E3D73")      # Navy Blue
    c_gold = colors.HexColor("#B45309")      # Deep Amber Gold
    c_dark = colors.HexColor("#0F172A")      # Dark Slate
    c_muted = colors.HexColor("#475569")     # Muted text
    c_bg_light = colors.HexColor("#F8FAFC")  # Light gray
    c_border = colors.HexColor("#E2E8F0")    # Border line
    c_green = colors.HexColor("#047857")     # Emerald
    
    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_muted,
        spaceAfter=14
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_blue,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_dark
    )

    dialogue_kanishk = ParagraphStyle(
        'DialogueK',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E40AF") # Royal Blue
    )

    dialogue_vibhor = ParagraphStyle(
        'DialogueV',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#7E22CE") # Vibrant Purple
    )

    script_text = ParagraphStyle(
        'ScriptText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=c_dark
    )

    action_text = ParagraphStyle(
        'ActionText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F766E") # Teal
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=0
    )

    story = []

    # ------------------ COVER / TITLE BANNER ------------------
    badge_data = [[
        Paragraph("<font color='#B45309'><b>OFFICIAL PROJECT PRESENTATION &amp; DEFENSE PLAYBOOK</b></font>", ParagraphStyle('Bdg', fontName='Helvetica-Bold', fontSize=8, textColor=c_gold, alignment=1)),
        Paragraph("<font color='#047857'><b>LIVE PRODUCTION BUILD</b></font>", ParagraphStyle('Bdg2', fontName='Helvetica-Bold', fontSize=8, textColor=c_green, alignment=1))
    ]]
    badge_table = Table(badge_data, colWidths=[330, 157])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#FEF3C7")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#D1FAE5")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (0, 0), 0.5, colors.HexColor("#F59E0B")),
        ('BOX', (1, 0), (1, 0), 0.5, colors.HexColor("#10B981")),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("GH Raisoni College AI Campus Assistant", title_style))
    story.append(Paragraph("A Conversational Campus Intelligence System &amp; Smart Student Utility Suite<br/><b>Institution:</b> GH Raisoni International Skill Tech University, Pune &bull; <b>URL:</b> https://college-ai-chatbot-c94w.onrender.com", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=10))

    # ------------------ TEAM ROLES & OWNERSHIP ------------------
    story.append(Paragraph("1. Team Division &amp; Core Architecture Responsibilities", h1_style))
    
    roles_data = [
        [
            Paragraph("<b>Team Member</b>", table_header),
            Paragraph("<b>Core Role &amp; Focus Area</b>", table_header),
            Paragraph("<b>Assigned Modules &amp; Technical Deliverables</b>", table_header)
        ],
        [
            Paragraph("<b>Kanishk Singh</b><br/><font size='7.5' color='#1E40AF'>Backend &amp; Logic Lead</font>", body_bold),
            Paragraph("Backend Engine, Database Models, Academic Policy Algorithms &amp; API Security", body_style),
            Paragraph("&bull; Python Flask Server Architecture &amp; REST Routing<br/>"
                      "&bull; SQLite Relational Schema &amp; Session Authentication<br/>"
                      "&bull; <b>Smart Bunk Calculator Algorithm</b> (75% SPPU policy math)<br/>"
                      "&bull; Hybrid AI Fallback (Deterministic DB + Google Gemini API)<br/>"
                      "&bull; Faculty Admin Dashboard &amp; Unanswered FAQ Queue<br/>"
                      "&bull; Parameterized Query Security &amp; Data Integrity", body_style)
        ],
        [
            Paragraph("<b>Vibhor Saini</b><br/><font size='7.5' color='#7E22CE'>Frontend &amp; UX Lead</font>", body_bold),
            Paragraph("User Interface, Glassmorphism Design System, Animations &amp; Accessibility", body_style),
            Paragraph("&bull; Modern Cyber-Navy &amp; Light Glassmorphism UI System<br/>"
                      "&bull; <b>Multilingual Selector</b> (English, Marathi, Hindi)<br/>"
                      "&bull; Web Speech API Integration (Voice STT &amp; Audio TTS)<br/>"
                      "&bull; <b>3D Interactive Digital ID Pass</b> (Holographic Flip &amp; QR)<br/>"
                      "&bull; Instant Bonafide / NOC Certificate Print Stylesheet<br/>"
                      "&bull; Campus Floor Navigator &amp; Emergency SOS Speed-Dial", body_style)
        ]
    ]
    t_roles = Table(roles_data, colWidths=[105, 125, 257])
    t_roles.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (0, 2), (-1, 2), colors.white),
    ]))
    story.append(t_roles)
    story.append(Spacer(1, 10))

    # ------------------ USPs (UNIQUE SELLING PROPOSITIONS) ------------------
    story.append(Paragraph("2. Unique Selling Propositions (USPs) — Why This Outperforms College ERPs", h1_style))
    story.append(Paragraph("Traditional ERP portals (such as CyberVidya) function as static administrative record vaults. Our solution delivers 6 breakthrough advantages that elevate student experience:", body_style))

    usps_data = [
        [
            Paragraph("<b>#</b>", table_header),
            Paragraph("<b>Breakthrough USP</b>", table_header),
            Paragraph("<b>Official ERP (CyberVidya) Reality</b>", table_header),
            Paragraph("<b>Our AI Campus Assistant Innovation</b>", table_header)
        ],
        [
            Paragraph("<b>USP 1</b>", body_bold),
            Paragraph("<b>Proactive Attendance Intelligence vs. Static Data</b>", body_style),
            Paragraph("Displays flat numbers (e.g. <i>'Principles of Marketing: 22%'</i>) with <b>zero warning</b> or actionable advice.", body_style),
            Paragraph("<b>Automated Detention Forecasting:</b> Flags detention danger instantly, calculates permissible safe bunks, or calculates exact consecutive classes required to escape detention.", body_style)
        ],
        [
            Paragraph("<b>USP 2</b>", body_bold),
            Paragraph("<b>1-Second Natural Discovery vs. 8-Click Menus</b>", body_style),
            Paragraph("Requires navigating up to 8 nested accordion dropdowns (e.g. <i>Attendance &rarr; My Calendar &rarr; Date Filter &rarr; 15-min Slot Grid</i>).", body_style),
            Paragraph("<b>Instant Conversational Answer:</b> Student types or speaks <i>'When is my next exam?'</i> or <i>'Where is Web Lab?'</i> and receives instant verified answer in 1 second.", body_style)
        ],
        [
            Paragraph("<b>USP 3</b>", body_bold),
            Paragraph("<b>Self-Service Document Generation</b>", body_style),
            Paragraph("Students must submit physical paper requisition slips and wait 3&ndash;5 working days for admin sign-off.", body_style),
            Paragraph("<b>1-Click Printable Bonafide / NOC:</b> Automatically generates verified university letter with seal, roll number, and signature lines ready for instant PDF download.", body_style)
        ],
        [
            Paragraph("<b>USP 4</b>", body_bold),
            Paragraph("<b>Inclusive Multilingual &amp; Voice Accessibility</b>", body_style),
            Paragraph("Strictly English-only, desktop-oriented web layout with heavy horizontal data scrolling.", body_style),
            Paragraph("<b>Trilingual (EN / MR / HI) Voice System:</b> Eliminates language barriers for regional students and parents with speech-to-text input and audio readout.", body_style)
        ],
        [
            Paragraph("<b>USP 5</b>", body_bold),
            Paragraph("<b>Faculty Feedback Loop &amp; Knowledge Self-Correction</b>", body_style),
            Paragraph("Student grievances or confusion on rules are lost with zero telemetry on what students are asking.", body_style),
            Paragraph("<b>Unanswered FAQ Queue in Admin:</b> Captures queries the bot could not resolve, giving faculty a 1-click interface to update institutional data continuously.", body_style)
        ],
        [
            Paragraph("<b>USP 6</b>", body_bold),
            Paragraph("<b>3D Digital Campus Identity &amp; Safety Hub</b>", body_style),
            Paragraph("Plastic physical ID cards or plain static profile text; no built-in campus safety tools.", body_style),
            Paragraph("<b>Interactive 3D ID Pass &amp; SOS Dial:</b> Holographic flippable student pass with QR code, paired with speed-dial helplines for campus security and anti-ragging.", body_style)
        ]
    ]
    t_usps = Table(usps_data, colWidths=[38, 114, 155, 180])
    t_usps.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_blue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_usps)
    
    story.append(PageBreak()) # Clean page 2 break

    # ------------------ 5-MINUTE PRESENTATION SCRIPT ------------------
    story.append(Paragraph("3. Step-by-Step 5-Minute Presentation Script (Turn-by-Turn Dialogue)", h1_style))
    story.append(Paragraph("Follow this turn-by-turn script during the evaluation. When one person speaks, the other drives the mouse/screen seamlessly.", body_style))

    script_data = [
        [
            Paragraph("<b>Time &amp; Phase</b>", table_header),
            Paragraph("<b>Speaker &amp; Dialogue Script</b>", table_header),
            Paragraph("<b>On-Screen Action (Teammate Task)</b>", table_header)
        ],
        [
            Paragraph("<b>[0:00 - 0:45]</b><br/>The Hook &amp; Problem", body_bold),
            Paragraph("<b>Vibhor (Frontend Lead):</b><br/>"
                      "<font size='8'><i>\"Good morning Ma'am/Sir. In university life, students constantly struggle with administrative ERPs like CyberVidya. Finding simple timetable or attendance data takes up to 8 clicks, tables break on mobile, and students never get answers to real questions like 'Can I bunk?' or 'Where is my exam room?'. We built the <b>GH Raisoni College AI Assistant</b> to give students instant answers and smart self-service tools.\"</i></font>", dialogue_vibhor),
            Paragraph("<b>Kanishk:</b> Displays the clean homepage on screen (https://college-ai-chatbot-c94w.onrender.com). Shows the authentic vibrant college purple-gold logo and hero service cards.", action_text)
        ],
        [
            Paragraph("<b>[0:45 - 1:45]</b><br/>UI &amp; Multilingual Voice", body_bold),
            Paragraph("<b>Vibhor:</b><br/>"
                      "<font size='8'><i>\"I led the Frontend and UX engineering. We designed a responsive Glassmorphism interface with dark/light themes. For regional accessibility, we integrated English, Marathi, and Hindi. Notice how switching to Marathi immediately adapts the UI and lets students ask 'फीस किती आहे?' or use the Web Speech microphone to dictate queries verbally.\"</i></font>", dialogue_vibhor),
            Paragraph("<b>Kanishk:</b> Clicks the <b>मराठी</b> pill in the header, demonstrates the active language toggle, clicks the <b>🎙️ Mic button</b> to show speech recognition audio waves, and tests a quick query.", action_text)
        ],
        [
            Paragraph("<b>[1:45 - 2:00]</b><br/>Smooth Hand-Off", body_bold),
            Paragraph("<b>Vibhor:</b><br/>"
                      "<font size='8'><i>\"Now, my teammate Kanishk will walk you through our core backend architecture, authenticated student records, and the academic policy engine.\"</i></font>", dialogue_vibhor),
            Paragraph("<b>Kanishk steps to front.</b> Vibhor seamlessly takes over the laptop keyboard and mouse.", action_text)
        ],
        [
            Paragraph("<b>[2:00 - 3:15]</b><br/>Smart Bunk &amp; Policy Math", body_bold),
            Paragraph("<b>Kanishk (Backend Lead):</b><br/>"
                      "<font size='8'><i>\"Thank you Vibhor. I architected the Python Flask server, relational SQLite models, and university policy logic. Once a student signs in [e.g. Aarav - 86.5% attendance], asking <b>'Can I bunk?'</b> doesn't give a flat number &mdash; it executes our SPPU 75% mathematical engine, confirming Aarav can safely miss up to 6 lectures.<br/>"
                      "If a student is below 75%, our algorithm switches to <b>Recovery Mode</b>, forecasting the exact consecutive classes needed to escape detention!\"</i></font>", dialogue_kanishk),
            Paragraph("<b>Vibhor:</b> Clicks <b>Student Login</b>, selects <b>ISTU00000001</b>, types <b>'Can I bunk?'</b>, then clicks the <b>🎯 Open Interactive Bunk Tool</b> button in the message to display the animated radial gauge.", action_text)
        ],
        [
            Paragraph("<b>[3:15 - 4:00]</b><br/>3D ID &amp; Instant Bonafide", body_bold),
            Paragraph("<b>Kanishk:</b><br/>"
                      "<font size='8'><i>\"We also replaced manual administrative paperwork. By typing <b>'Generate bonafide certificate'</b>, the backend pulls the student's active semester credentials, and Vibhor's print stylesheet formats a university-grade NOC/Bonafide certificate with college seal ready for instant PDF submission. Students can also access their 3D flippable digital ID pass with verified QR code.\"</i></font>", dialogue_kanishk),
            Paragraph("<b>Vibhor:</b> Types <b>'Generate bonafide certificate'</b> to trigger the modal, shows the Print/PDF button, then clicks the student ID badge to demonstrate the 3D card holographic flip.", action_text)
        ],
        [
            Paragraph("<b>[4:00 - 4:30]</b><br/>Admin Portal &amp; Telemetry", body_bold),
            Paragraph("<b>Kanishk:</b><br/>"
                      "<font size='8'><i>\"Finally, for college administrators, we built a dedicated <b>Admin Command Center</b> at `/admin`. Faculty can add new FAQs without touching code, view unanswered questions logged by the AI, and audit student query trends to continuously refine campus information.\"</i></font>", dialogue_kanishk),
            Paragraph("<b>Vibhor:</b> Opens the `/admin` tab, logs in with `admin/admin123`, highlights the knowledge base table and the missing question queue.", action_text)
        ],
        [
            Paragraph("<b>[4:30 - 5:00]</b><br/>Conclusion &amp; Viva Ready", body_bold),
            Paragraph("<b>Vibhor &amp; Kanishk:</b><br/>"
                      "<font size='8'><i>\"In conclusion, our project bridges student engagement with institutional governance. It is live in production on Render. Thank you Ma'am/Sir, we are now eager to take your questions!\"</i></font>", body_bold),
            Paragraph("Both stand side-by-side, attentive, confident, and ready for viva questions.", action_text)
        ]
    ]
    t_script = Table(script_data, colWidths=[80, 240, 167])
    t_script.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_script)
    
    story.append(PageBreak()) # Clean page 3 break

    # ------------------ EXCITING FUTURE IMPLEMENTATIONS ------------------
    story.append(Paragraph("4. High-Impact Future Implementations (Next Phase Roadmap)", h1_style))
    story.append(Paragraph("To demonstrate technical foresight to your teachers, present these 6 cutting-edge engineering extensions planned for the production roadmap:", body_style))

    future_data = [
        [
            Paragraph("<b>#</b>", table_header),
            Paragraph("<b>Planned Innovation</b>", table_header),
            Paragraph("<b>Technical Implementation Details &amp; Value Proposition</b>", table_header)
        ],
        [
            Paragraph("<b>1</b>", body_bold),
            Paragraph("<b>Automated CyberVidya ERP Live Sync via Webhooks</b>", body_style),
            Paragraph("Establish real-time bidirectional synchronization with university CyberVidya Oracle/PostgreSQL databases via authenticated REST webhooks or headless ETL workers. Updates attendance and exam scores without manual database entry.", body_style)
        ],
        [
            Paragraph("<b>2</b>", body_bold),
            Paragraph("<b>WhatsApp &amp; Telegram Bot Gateway</b>", body_style),
            Paragraph("Deploy an omnichannel Twilio / Meta Cloud API webhook gateway. Allows students to send a quick WhatsApp message (e.g. <i>'Can I bunk Data Structure today?'</i>) and receive an instant reply without opening a browser.", body_style)
        ],
        [
            Paragraph("<b>3</b>", body_bold),
            Paragraph("<b>AI Exam Paper Predictor &amp; Topic Heatmap</b>", body_style),
            Paragraph("Integrate a fine-tuned LLM that ingests previous 5 years' SPPU and Raisoni question papers to identify recurring chapter weightages, generating personalized high-probability revision flashcards for each student.", body_style)
        ],
        [
            Paragraph("<b>4</b>", body_bold),
            Paragraph("<b>Calendar Sync with Push Notifications</b>", body_style),
            Paragraph("Generate dynamic <code>.ics</code> calendar subscriptions for Google Calendar and Apple Calendar. Automatically alerts students 15 minutes before practical exam submissions or timetable changes.", body_style)
        ],
        [
            Paragraph("<b>5</b>", body_bold),
            Paragraph("<b>Augmented Reality (AR) Campus Wayfinding</b>", body_style),
            Paragraph("Utilize WebXR and smartphone cameras to superimpose 3D holographic directional arrows in college hallways, guiding newly admitted students and guests directly to laboratories, dean offices, or seminar halls.", body_style)
        ],
        [
            Paragraph("<b>6</b>", body_bold),
            Paragraph("<b>Campus Mental Health &amp; Peer Copilot</b>", body_style),
            Paragraph("Implement a safe, ethically fine-tuned psychological first-aid copilot trained on academic anxiety management, providing confidential stress-relief prompts and direct linkage to college counseling cell.", body_style)
        ]
    ]
    t_future = Table(future_data, colWidths=[24, 155, 308])
    t_future.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_blue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_future)
    story.append(Spacer(1, 10))

    # ------------------ VIVA DEFENSE GUIDE ------------------
    story.append(Paragraph("5. Anticipated Teacher Viva Questions &amp; Winning Answers", h1_style))
    
    viva_data = [
        [
            Paragraph("<b>Question Topic</b>", table_header),
            Paragraph("<b>Assigned Answerer</b>", table_header),
            Paragraph("<b>Exact Technical Answer to Deliver</b>", table_header)
        ],
        [
            Paragraph("<b>\"How does the Bunk Calculator formula work?\"</b>", body_bold),
            Paragraph("<b>Kanishk</b><br/><font size='7' color='#1E40AF'>Backend Lead</font>", body_bold),
            Paragraph("<i>\"We enforce the 75% SPPU threshold with two distinct formulas:<br/>"
                      "1. <b>Safe Bunks:</b> &lfloor; (Attended - 0.75 &times; Total) / 0.75 &rfloor;.<br/>"
                      "2. <b>Recovery Target:</b> If attendance &lt; 75%, classes needed = &lceil; (0.75 &times; Total - Attended) / 0.25 &rceil;. It simulates future outcomes without altering raw records.\"</i>", body_style)
        ],
        [
            Paragraph("<b>\"How did you build the UI and ensure mobile responsiveness?\"</b>", body_bold),
            Paragraph("<b>Vibhor</b><br/><font size='7' color='#7E22CE'>Frontend Lead</font>", body_bold),
            Paragraph("<i>\"We avoided heavy third-party CSS frameworks that bloat load times. We built a custom CSS3 Glassmorphism design system using CSS Grid, Flexbox, media queries for 320px to 4K displays, and PWA manifest for native app feel on mobile.\"</i>", body_style)
        ],
        [
            Paragraph("<b>\"How is the system secured against SQL Injection?\"</b>", body_bold),
            Paragraph("<b>Kanishk</b><br/><font size='7' color='#1E40AF'>Backend Lead</font>", body_bold),
            Paragraph("<i>\"All SQLite database queries utilize parameterized queries (`cursor.execute('SELECT ... WHERE roll_no = ?', (roll_no,))`). User inputs are never concatenated directly into SQL strings, preventing injection attacks entirely.\"</i>", body_style)
        ],
        [
            Paragraph("<b>\"How is voice input and multilingual handled?\"</b>", body_bold),
            Paragraph("<b>Vibhor</b><br/><font size='7' color='#7E22CE'>Frontend Lead</font>", body_bold),
            Paragraph("<i>\"We utilize the browser's native `webkitSpeechRecognition` and `speechSynthesis` APIs. For Marathi and Hindi, our client-side I18N dictionary dynamically translates UI strings and decodes phonetic regional queries.\"</i>", body_style)
        ]
    ]
    t_viva = Table(viva_data, colWidths=[120, 80, 287])
    t_viva.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_viva)
    story.append(Spacer(1, 10))

    # ------------------ PRE-DEMO CHEAT SHEET ------------------
    story.append(Paragraph("6. Pre-Presentation Emergency Cheat Sheet", h1_style))
    cheat_box = [
        [
            Paragraph("<b>Live URL:</b> https://college-ai-chatbot-c94w.onrender.com &bull; <b>Admin:</b> User: <code>admin</code> | Pass: <code>admin123</code><br/>"
                      "<b>Demo Student Logins:</b> <code>ISTU00000001</code> (Aarav - 86.5%, Safe Bunks) &bull; <code>ISTU00000003</code> (Rohan - 67.5%, Detention Warning)<br/>"
                      "<b>Key Demo Queries:</b> <i>'Can I bunk?'</i>, <i>'Generate bonafide certificate'</i>, <i>'Where is Web Lab?'</i>, <i>'फीस किती आहे?'</i>", body_style)
        ]
    ]
    t_cheat = Table(cheat_box, colWidths=[487])
    t_cheat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#3B82F6")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_cheat)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✓ PDF successfully created: {filename}")

if __name__ == '__main__':
    out_pdf = 'static/downloads/GH_Raisoni_AI_Chatbot_Presentation_Playbook.pdf'
    build_pdf(out_pdf)
