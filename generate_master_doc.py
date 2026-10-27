import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def style_table(table, col_widths=None, header_bg="1B365D", alt_bg="F8FAFC"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        is_header = (i == 0)
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if is_header:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

        for j, cell in enumerate(row.cells):
            set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
            if col_widths and j < len(col_widths):
                cell.width = Inches(col_widths[j])
            
            if is_header:
                set_cell_background(cell, header_bg)
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(9.5)
                        run.font.name = "Calibri"
            else:
                if i % 2 == 1:
                    set_cell_background(cell, "FFFFFF")
                else:
                    set_cell_background(cell, alt_bg)
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        run.font.name = "Calibri"

def add_callout(doc, text, title="NOTE / DBMS INSIGHT"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"📌 {title}: ")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = RGBColor(37, 99, 235)
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(9.5)
    r_text.font.italic = True
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "0F172A")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(code_text)
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(226, 232, 240)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def create_document():
    doc = docx.Document()

    # Page setup - 0.75 in margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Palette
    NAVY = RGBColor(27, 54, 93)     # #1B365D
    BLUE = RGBColor(37, 99, 235)    # #2563EB
    DARK = RGBColor(30, 41, 59)     # #1E293B

    # ==========================================
    # COVER / HEADER
    # ==========================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(2)
    r_inst = p_title.add_run("AMRITA VISHWA VIDYAPEETHAM\nAmrita School of Computing · Department of Computer Science & Engineering\n")
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(12)
    r_inst.font.bold = True
    r_inst.font.color.rgb = NAVY

    r_course = p_title.add_run("Course: 23CSE202 — Database Management Systems (DBMS)\nAcademic Year: 2025–2026 · Group C9\n\n")
    r_course.font.name = "Calibri"
    r_course.font.size = Pt(11)
    r_course.font.color.rgb = BLUE

    r_main = p_title.add_run("HostelOS: Relational Database System\n")
    r_main.font.name = "Calibri"
    r_main.font.size = Pt(24)
    r_main.font.bold = True
    r_main.font.color.rgb = NAVY

    r_sub = p_title.add_run("Complete End-to-End System Documentation, Normalization Proofs, Data Dictionary & Viva Master Guide\n")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Team Members Table
    t_team = doc.add_table(rows=5, cols=4)
    headers = ["Team Member Name", "Roll Number", "Academic Subsystem Ownership", "Assigned Project Part"]
    for j, h in enumerate(headers):
        t_team.cell(0, j).paragraphs[0].text = h
    
    team_data = [
        ("Siddharth Sai", "AM.SC.U4CSE25209", "Database Architecture, Security & Authentication", "Person 1 (Architect)"),
        ("Gowtham Adithya", "AM.SC.U4CSE25258", "Accommodation & Room Allocation Engine", "Person 2 (Rooms Lead)"),
        ("Rama Sri Surya", "AM.SC.U4CSE25263", "Maintenance Workforce & Grievance Ticketing", "Person 3 (Workforce Lead)"),
        ("Sai Santhosh", "AM.SC.U4CSE25264", "Student Welfare, Leave Passes & Night Attendance", "Person 4 (Welfare Lead)")
    ]
    for i, row in enumerate(team_data):
        for j, val in enumerate(row):
            t_team.cell(i+1, j).paragraphs[0].text = val
    
    style_table(t_team, col_widths=[1.8, 1.8, 2.4, 1.5])
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Helper function for Section Headings
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = BLUE
        return p

    def add_body(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = DARK
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = DARK
        return p

    # ==========================================
    # SECTION 1: EXECUTIVE PROJECT SUMMARY
    # ==========================================
    add_h1("1. Executive Project Summary & Abstract")
    add_body(
        "HostelOS is an enterprise relational database system engineered to automate campus accommodation operations. "
        "Traditional hostel management relies on fragmented paper registers or disconnected spreadsheets, resulting in critical operational flaws: "
        "(1) room overbooking exceeding physical bed capacity, (2) untracked student night out-passes and gate pass return dates, "
        "(3) slow turnaround and lack of accountability for maintenance grievances, and (4) severe data anomalies due to unnormalized functional dependencies. "
        "HostelOS eliminates these liabilities through a 10-table relational schema designed strictly in Boyce-Codd Normal Form (BCNF), "
        "enforcing referential integrity, automated check constraints, composite uniqueness, and multi-tier Role-Based Access Control (RBAC)."
    )
    add_callout(doc, "HostelOS is fully implemented with a React 18 frontend, Python FastAPI backend, SQLAlchemy 2.0 ORM, and PostgreSQL 14+ / SQLite engine.", "FULL-STACK CAPABILITY")

    # ==========================================
    # SECTION 2: 4-MEMBER WORK DIVISION & PRESENTATION
    # ==========================================
    add_h1("2. 4-Member Work Division & Viva Presentation Guide")
    add_body(
        "To ensure balanced evaluation during the viva and academic defense, the project is divided into four equal vertical slices. "
        "Each team member commands their respective database tables, backend API endpoints, frontend interfaces, and theoretical DBMS concepts."
    )

    t_matrix = doc.add_table(rows=5, cols=5)
    headers_matrix = ["Member", "Assigned Module", "Database Tables", "Backend APIs", "Core DBMS Concepts"]
    for j, h in enumerate(headers_matrix):
        t_matrix.cell(0, j).paragraphs[0].text = h
    
    matrix_data = [
        ("Person 1\n(Siddharth)", "Architecture & Auth", "STUDENT, ADMIN\n(+ Overall Schema)", "routers/auth.py", "ER Modeling, BCNF Proofs, B-Tree Indexes, RBAC"),
        ("Person 2\n(Gowtham)", "Rooms & Allocation", "ROOM_TYPE, ROOM, ALLOCATION", "routers/rooms.py", "M:N Associative Tables, Capacity Checks, Row Locks"),
        ("Person 3\n(Surya)", "Workforce & Complaints", "STAFF, AUTHORITY, COMPLAINT", "routers/complaints.py", "Nullable FKs, ON DELETE SET NULL, State Machine"),
        ("Person 4\n(Santhosh)", "Welfare & Attendance", "LEAVE_PASS, ATTENDANCE", "routers/leaves.py\nrouters/attendance.py", "Idempotent Unique Keys, Date Checks, Aggregations")
    ]
    for i, row in enumerate(matrix_data):
        for j, val in enumerate(row):
            t_matrix.cell(i+1, j).paragraphs[0].text = val
    
    style_table(t_matrix, col_widths=[1.3, 1.4, 1.8, 1.4, 1.6])
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("2.1 Team Viva Speaking Script (5-Minute Coordinated Demo)")
    add_body("1. Person 1 (Opening & Blueprint): Displays the Schema Diagram. Explains how 10 entities interact, justifies surrogate integer keys, and proves BCNF normalization. Logs into the portal to demonstrate authentication.", "Speaker 1 Script: ")
    add_body("2. Person 2 (Accommodation Engine): Demonstrates RoomAllocation.jsx. Shows how rooms in Block A/B/C are categorized by capacity, and walks through an allocation transaction proving overbooking is mathematically prevented.", "Speaker 2 Script: ")
    add_body("3. Person 3 (Maintenance & Workforce): Demonstrates RegisterComplaint.jsx and ComplaintManagement.jsx. Explains ticket generation, staff assignment, nullable FK semantics, and ON DELETE SET NULL for audit retention.", "Speaker 3 Script: ")
    add_body("4. Person 4 (Safety, Passes & Roll Call): Demonstrates ApplyLeave.jsx, LeaveTracking.jsx, and AttendanceRegister.jsx. Shows idempotent daily attendance, automatic synchronization with approved leaves, and analytics charts in Overview.jsx.", "Speaker 4 Script: ")

    # ==========================================
    # SECTION 3: SYSTEM ARCHITECTURE & ER MODEL
    # ==========================================
    add_h1("3. System Architecture & Entity-Relationship (ER) Model")
    add_body(
        "HostelOS implements the classic 3-Tier ANSI/SPARC Database Architecture:\n"
        "• Tier 1 (Presentation): React 18, Vite, Tailwind CSS with responsive mobile-ready cards.\n"
        "• Tier 2 (Application / Business Logic): Python FastAPI providing high-throughput asynchronous REST APIs with Pydantic validation schemas.\n"
        "• Tier 3 (Database / Storage): PostgreSQL 14+ relational engine enforcing relational constraints, write-ahead logging (WAL), and ACID transactions."
    )

    add_h2("3.1 Official 10-Table Relational Schema Diagram")
    diagram_path = os.path.join(os.getcwd(), "schema_diagram.png")
    if os.path.exists(diagram_path):
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(diagram_path, width=Inches(6.5))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figure 3.1: Official 10-Table Normalized Relational Schema & Crow's Foot ER Diagram (HostelOS)")
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(100, 116, 139)

    add_body(
        "Key Entity-Relationship Cardinalities:\n"
        "• ROOM_TYPE to ROOM (1:N): One room type categorizes many individual physical rooms.\n"
        "• ROOM & STUDENT to ALLOCATION (M:N resolved via Associative Table): Resolves multi-semester room allocations.\n"
        "• STUDENT to COMPLAINT (1:N) & STAFF to COMPLAINT (1:N, Partial): Student reports grievance; staff technician is dispatched.\n"
        "• STUDENT to LEAVE_PASS (1:N) & AUTHORITY to LEAVE_PASS (1:N): Student applies for leave; warden reviews and issues gate pass.\n"
        "• STUDENT to ATTENDANCE (1:N) & ADMIN to ATTENDANCE (1:N): Admin logs nightly roll call."
    )

    # ==========================================
    # SECTION 4: DATA DICTIONARY & SAMPLE DATA (ALL 10 TABLES)
    # ==========================================
    add_h1("4. Relational Data Dictionary & Realistic Sample Data Tables")

    # Helper for adding table specs
    def add_table_section(tbl_num, name, module_person, purpose, dict_headers, dict_rows, sample_headers, sample_rows, col_w_dict=None, col_w_sample=None):
        add_h2(f"Table {tbl_num}: {name} ({module_person})")
        add_body(purpose, "ELI5 Purpose: ")

        # Data Dictionary Table
        doc.add_paragraph().paragraph_format.space_after = Pt(1)
        p_lbl1 = doc.add_paragraph()
        p_lbl1.paragraph_format.keep_with_next = True
        r_l1 = p_lbl1.add_run(f"Data Dictionary — Schema Definition ({name})")
        r_l1.font.bold = True
        r_l1.font.size = Pt(9.5)
        r_l1.font.color.rgb = NAVY

        t_dict = doc.add_table(rows=len(dict_rows)+1, cols=len(dict_headers))
        for j, h in enumerate(dict_headers):
            t_dict.cell(0, j).paragraphs[0].text = h
        for i, row in enumerate(dict_rows):
            for j, val in enumerate(row):
                t_dict.cell(i+1, j).paragraphs[0].text = val
        style_table(t_dict, col_widths=col_w_dict or [1.4, 1.4, 2.0, 2.7])
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

        # Sample Data Table
        p_lbl2 = doc.add_paragraph()
        p_lbl2.paragraph_format.keep_with_next = True
        r_l2 = p_lbl2.add_run(f"Sample Data Example — Actual Stored Records ({name})")
        r_l2.font.bold = True
        r_l2.font.size = Pt(9.5)
        r_l2.font.color.rgb = BLUE

        t_samp = doc.add_table(rows=len(sample_rows)+1, cols=len(sample_headers))
        for j, h in enumerate(sample_headers):
            t_samp.cell(0, j).paragraphs[0].text = h
        for i, row in enumerate(sample_rows):
            for j, val in enumerate(row):
                t_samp.cell(i+1, j).paragraphs[0].text = val
        style_table(t_samp, col_widths=col_w_sample or [1.0, 2.0, 1.5, 3.0])
        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Table 1: ROOM_TYPE
    add_table_section(
        1, "room_types", "Person 2 — Rooms Module",
        "Master room catalog defining configurations and physical bed capacities so capacities are never duplicated.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique identifier for room category"],
            ["type_name", "VARCHAR(100)", "UNIQUE, NOT NULL", "Display name (e.g., 'Single AC', 'Double Non-AC')"],
            ["capacity", "INTEGER", "NOT NULL, CHECK (capacity > 0)", "Max allowable resident beds in this room type"]
        ],
        ["id", "type_name", "capacity", "Notes"],
        [
            ["1", "Single Deluxe AC", "1", "Single student private quarters"],
            ["2", "Double Sharing Standard", "2", "Standard dual occupancy room"],
            ["3", "Triple Non-AC Economy", "3", "Triple sharing accommodation"],
            ["4", "Four-Bed Dormitory", "4", "Quad sharing layout"]
        ],
        col_w_dict=[1.4, 1.4, 2.2, 2.5],
        col_w_sample=[0.8, 2.4, 1.2, 3.1]
    )

    # Table 2: ROOM
    add_table_section(
        2, "rooms", "Person 2 — Rooms Module",
        "Represents individual physical rooms on campus across blocks, wings, and floors.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique room identifier"],
            ["block", "VARCHAR(50)", "NOT NULL", "Hostel block name (e.g., 'Block-A', 'Block-B')"],
            ["room_number", "VARCHAR(50)", "NOT NULL", "Door number (e.g., '101', '205')"],
            ["type_id", "INTEGER", "FK -> room_types(id), ON DELETE RESTRICT", "Links room to bed capacity configuration"],
            ["has_ac", "BOOLEAN", "NOT NULL, DEFAULT FALSE", "Air-conditioning hardware installation flag"],
            ["created_at", "TIMESTAMP", "NOT NULL, DEFAULT CURRENT_TIMESTAMP", "Timestamp when room was added to inventory"]
        ],
        ["id", "block", "room_number", "type_id", "has_ac", "created_at"],
        [
            ["101", "Block-A", "101", "2 (Double)", "TRUE", "2026-08-01 09:00:00"],
            ["102", "Block-A", "102", "2 (Double)", "FALSE", "2026-08-01 09:00:00"],
            ["103", "Block-B", "205", "1 (Single)", "TRUE", "2026-08-01 09:15:00"],
            ["104", "Block-C", "310", "4 (Four-Bed)", "FALSE", "2026-08-01 09:30:00"]
        ],
        col_w_dict=[1.3, 1.3, 2.4, 2.5],
        col_w_sample=[0.7, 1.2, 1.2, 1.2, 1.0, 2.2]
    )

    # Table 3: ALLOCATION
    add_table_section(
        3, "allocations", "Person 2 — Rooms Module",
        "Associative junction table resolving student-to-room occupancy over multi-year campus residency.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique allocation ID"],
            ["student_id", "INTEGER", "FK -> students(id), ON DELETE CASCADE", "The student assigned to the bed"],
            ["room_id", "INTEGER", "FK -> rooms(id), ON DELETE CASCADE", "The assigned physical room"],
            ["allocation_date", "DATE", "NOT NULL, DEFAULT CURRENT_DATE", "Date occupancy commenced"],
            ["deposit_paid", "NUMERIC(10,2)", "NOT NULL, DEFAULT 5000.00", "Hostel maintenance caution deposit paid"],
            ["is_active", "BOOLEAN", "NOT NULL, DEFAULT TRUE", "TRUE = Current resident; FALSE = Vacated history"],
            ["created_at", "TIMESTAMP", "NOT NULL, DEFAULT CURRENT_TIMESTAMP", "Audit timestamp of transaction"]
        ],
        ["id", "student_id", "room_id", "allocation_date", "deposit_paid", "is_active"],
        [
            ["1", "1 (Siddharth)", "101", "2026-08-10", "₹5,000.00", "TRUE"],
            ["2", "2 (Gowtham)", "101", "2026-08-10", "₹5,000.00", "TRUE"],
            ["3", "3 (Surya)", "103", "2026-08-11", "₹7,500.00", "TRUE"],
            ["4", "4 (Santhosh)", "102", "2025-08-15", "₹5,000.00", "FALSE (Vacated)"]
        ],
        col_w_dict=[1.4, 1.3, 2.3, 2.5],
        col_w_sample=[0.6, 1.8, 0.9, 1.5, 1.3, 1.4]
    )

    # Table 4: STAFF
    add_table_section(
        4, "staff", "Person 3 — Workforce Module",
        "Directory of maintenance technicians dispatched to resolve electrical, plumbing, and carpentry grievances.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique staff identifier"],
            ["name", "VARCHAR(255)", "NOT NULL", "Full legal name of technician"],
            ["role_type", "VARCHAR(100)", "NOT NULL", "Specialization (Electrician, Plumber, Carpenter, etc.)"],
            ["phone", "VARCHAR(50)", "NOT NULL", "Emergency mobile contact for task dispatch"]
        ],
        ["id", "name", "role_type", "phone"],
        [
            ["1", "Ramesh Kumar", "Electrician", "+91 98450 11223"],
            ["2", "Suresh Nair", "Plumber", "+91 98450 44556"],
            ["3", "Murugan P.", "Carpenter", "+91 98450 77889"],
            ["4", "Selvam M.", "Housekeeping", "+91 98450 99001"]
        ],
        col_w_dict=[1.3, 1.3, 2.0, 2.9],
        col_w_sample=[0.8, 2.4, 2.0, 2.3]
    )

    # Table 5: AUTHORITY
    add_table_section(
        5, "authorities", "Person 3 — Workforce Module",
        "Hostel wardens and supervisors who approve leave passes and supervise maintenance.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique authority identifier"],
            ["name", "VARCHAR(255)", "NOT NULL", "Full legal name of warden/in-charge"],
            ["designation", "VARCHAR(100)", "NOT NULL, DEFAULT 'Chief Warden'", "Official administrative post"],
            ["email", "VARCHAR(255)", "UNIQUE, NOT NULL", "Official campus login email"],
            ["password_hash", "VARCHAR(255)", "NOT NULL", "Salted bcrypt encrypted authentication credential"],
            ["created_at", "TIMESTAMP", "NOT NULL, DEFAULT CURRENT_TIMESTAMP", "Account creation timestamp"]
        ],
        ["id", "name", "designation", "email", "password_hash"],
        [
            ["1", "Dr. K. Venkataraman", "Chief Warden", "warden@hostelos.in", "$2b$12$e8JkL..."],
            ["2", "Prof. Ananya Roy", "Deputy Warden (Girls)", "warden.girls@hostelos.in", "$2b$12$x9KlM..."],
            ["3", "Rajesh Balan", "Block Supervisor", "supervisor.b@hostelos.in", "$2b$12$p0QzR..."]
        ],
        col_w_dict=[1.4, 1.3, 2.2, 2.6],
        col_w_sample=[0.6, 2.2, 2.0, 2.0, 0.7]
    )

    # Table 6: COMPLAINT
    add_table_section(
        6, "complaints", "Person 3 — Workforce Module",
        "Complete grievance lifecycle ticketing system from student submission to technician resolution.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique internal ticket identifier"],
            ["ticket_number", "VARCHAR(50)", "UNIQUE, NOT NULL", "Public tracking token (e.g., 'TICK-2026-001')"],
            ["student_id", "INTEGER", "FK -> students(id), ON DELETE CASCADE", "Resident who filed the grievance"],
            ["staff_id", "INTEGER", "FK -> staff(id), ON DELETE SET NULL, Nullable", "Assigned technician (NULL when newly created)"],
            ["category", "VARCHAR(100)", "NOT NULL", "Issue trade (Electrical, Plumbing, Carpentry, etc.)"],
            ["title", "VARCHAR(200)", "NOT NULL", "Concise issue summary"],
            ["description", "TEXT", "NOT NULL", "Detailed breakdown of the problem"],
            ["urgency", "VARCHAR(20)", "CHECK IN ('High', 'Medium', 'Low')", "Priority rating of repair"],
            ["status", "VARCHAR(50)", "CHECK IN ('Open', 'Escalated', 'Resolved')", "Current ticket lifecycle state"],
            ["resolution_notes", "TEXT", "Nullable", "Technician work completion remarks"],
            ["image_url", "VARCHAR(500)", "Nullable", "Photo evidence of defective hardware"],
            ["created_at", "TIMESTAMP", "NOT NULL, DEFAULT CURRENT_TIMESTAMP", "Submission timestamp"],
            ["resolved_at", "TIMESTAMP", "Nullable", "Timestamp when closed by warden/staff"]
        ],
        ["id", "ticket_number", "student_id", "category", "urgency", "status", "resolved_at"],
        [
            ["1", "TICK-2026-001", "1", "Electrical", "Medium", "Resolved", "2026-09-02 14:30"],
            ["2", "TICK-2026-002", "2", "Plumbing", "High", "Resolved", "2026-09-05 11:15"],
            ["3", "TICK-2026-003", "3", "Carpentry", "Low", "Open", "NULL"]
        ],
        col_w_dict=[1.4, 1.3, 2.2, 2.6],
        col_w_sample=[0.6, 1.7, 1.1, 1.2, 1.0, 1.0, 1.3]
    )

    # Table 7: STUDENT
    add_table_section(
        7, "students", "Person 4 — Student Module",
        "Master student resident registry containing roll numbers, contact details, and encrypted auth credentials.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique student identifier"],
            ["roll_number", "VARCHAR(50)", "UNIQUE, NOT NULL", "University student roll code (e.g., 'AM.SC.U4CSE25209')"],
            ["name", "VARCHAR(255)", "NOT NULL", "Full legal name of resident"],
            ["major", "VARCHAR(255)", "NOT NULL, DEFAULT 'CSE'", "Branch and degree program"],
            ["emergency_contact", "VARCHAR(50)", "NOT NULL", "Parent or guardian emergency contact number"],
            ["email", "VARCHAR(255)", "UNIQUE, NOT NULL", "Institutional email for login and alerts"],
            ["password_hash", "VARCHAR(255)", "NOT NULL", "Salted bcrypt encrypted password hash"],
            ["created_at", "TIMESTAMP", "NOT NULL, DEFAULT CURRENT_TIMESTAMP", "Admission enrollment timestamp"]
        ],
        ["id", "roll_number", "name", "major", "emergency_contact", "email"],
        [
            ["1", "AM.SC.U4CSE25209", "Siddharth Sai", "CSE - AI", "+91 94441 23456", "siddharth@hostelos.in"],
            ["2", "AM.SC.U4CSE25258", "Gowtham Adithya", "CSE - Cyber", "+91 94442 34567", "gowtham@hostelos.in"],
            ["3", "AM.SC.U4CSE25263", "Rama Sri Surya", "CSE - Core", "+91 94443 45678", "surya@hostelos.in"],
            ["4", "AM.SC.U4CSE25264", "Sai Santhosh", "CSE - Core", "+91 94444 56789", "santhosh@hostelos.in"]
        ],
        col_w_dict=[1.4, 1.3, 2.2, 2.6],
        col_w_sample=[0.6, 1.7, 1.4, 1.2, 1.5, 1.6]
    )

    # Table 8: LEAVE_PASS
    add_table_section(
        8, "leave_passes", "Person 4 — Welfare Module",
        "Digital out-station permits, travel schedules, parental verification, and cryptographic gate tokens.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique pass identifier"],
            ["pass_code", "VARCHAR(50)", "UNIQUE, NOT NULL", "Human-readable pass code (e.g., 'PASS-8921')"],
            ["student_id", "INTEGER", "FK -> students(id), ON DELETE CASCADE", "Applicant resident"],
            ["authority_id", "INTEGER", "FK -> authorities(id), ON DELETE SET NULL, Nullable", "Warden who reviewed/approved request"],
            ["leave_type", "VARCHAR(50)", "CHECK IN ('Weekend outing', 'Emergency leave', 'Vacation')", "Permit category"],
            ["departure_date", "TIMESTAMP", "NOT NULL", "Scheduled exit timestamp through campus gate"],
            ["return_date", "TIMESTAMP", "NOT NULL", "Expected arrival timestamp back to hostel"],
            ["destination", "VARCHAR(255)", "NOT NULL", "Travel destination address / home town"],
            ["reason", "TEXT", "NOT NULL", "Detailed justification of leave"],
            ["emergency_contact", "VARCHAR(50)", "NOT NULL", "Verified parent telephone number"],
            ["parent_consent", "BOOLEAN", "NOT NULL, DEFAULT TRUE", "Parent approval verification flag"],
            ["status", "VARCHAR(50)", "CHECK IN ('Pending', 'Approved', 'Validated', ...)", "Gate pass state machine status"],
            ["gate_pass_token", "VARCHAR(100)", "Nullable", "Encrypted digital token scanned by gate guards"],
            ["created_at", "TIMESTAMP", "NOT NULL, DEFAULT CURRENT_TIMESTAMP", "Submission timestamp"],
            ["*Constraint*", "CHECK", "return_date >= departure_date", "Guarantees return is chronologically after departure"]
        ],
        ["id", "pass_code", "student_id", "leave_type", "departure_date", "return_date", "status"],
        [
            ["1", "PASS-8921", "1", "Weekend outing", "2026-10-10 17:00", "2026-10-12 20:00", "Approved"],
            ["2", "PASS-8922", "2", "Emergency leave", "2026-10-11 08:00", "2026-10-13 18:00", "Pending"],
            ["3", "PASS-8923", "3", "Vacation", "2026-10-01 06:00", "2026-10-06 21:00", "Returned"]
        ],
        col_w_dict=[1.4, 1.3, 2.2, 2.6],
        col_w_sample=[0.6, 1.3, 1.1, 1.4, 1.4, 1.4, 0.8]
    )

    # Table 9: ATTENDANCE
    add_table_section(
        9, "attendance", "Person 4 — Welfare Module",
        "Nightly roll-call register ensuring every student is physically accounted for before curfew.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique attendance identifier"],
            ["student_id", "INTEGER", "FK -> students(id), ON DELETE CASCADE", "Student undergoing roll call"],
            ["admin_id", "INTEGER", "FK -> admins(id), ON DELETE SET NULL, Nullable", "Staff/Admin logging attendance"],
            ["date", "DATE", "NOT NULL", "Calendar date of roll call"],
            ["status", "VARCHAR(50)", "CHECK IN ('Present', 'Absent', 'Late / Permitted')", "Presence audit flag"],
            ["notes", "VARCHAR(255)", "Nullable", "Remarks (e.g., 'Late lab approval')"],
            ["created_at", "TIMESTAMP", "NOT NULL, DEFAULT CURRENT_TIMESTAMP", "Log entry timestamp"],
            ["*Constraint*", "UNIQUE", "UNIQUE (student_id, date)", "Idempotency constraint: prevents duplicate daily marks"]
        ],
        ["id", "student_id", "date", "status", "notes", "created_at"],
        [
            ["1", "1 (Siddharth)", "2026-10-10", "Present", "In room during 9:30 PM roll call", "2026-10-10 21:35"],
            ["2", "2 (Gowtham)", "2026-10-10", "Present", "In room", "2026-10-10 21:36"],
            ["3", "3 (Surya)", "2026-10-10", "Late / Permitted", "Working in AI Lab with permission", "2026-10-10 21:38"],
            ["4", "4 (Santhosh)", "2026-10-10", "Absent", "Not in room; warden alerted", "2026-10-10 21:40"]
        ],
        col_w_dict=[1.4, 1.3, 2.2, 2.6],
        col_w_sample=[0.6, 1.5, 1.1, 1.4, 2.2, 1.2]
    )

    # Table 10: ADMIN
    add_table_section(
        10, "admins", "Person 1 — Security Module",
        "Superusers and institutional IT heads managing system configurations, backups, and user enrollments.",
        ["Column", "Data Type", "Constraints", "ELI5 Description"],
        [
            ["id", "SERIAL", "PRIMARY KEY", "Surrogate unique administrator identifier"],
            ["name", "VARCHAR(255)", "NOT NULL", "Full legal name of administrator"],
            ["email", "VARCHAR(255)", "UNIQUE, NOT NULL", "Master administrative login email"],
            ["password_hash", "VARCHAR(255)", "NOT NULL", "Salted bcrypt encrypted password hash"],
            ["created_at", "TIMESTAMP", "NOT NULL, DEFAULT CURRENT_TIMESTAMP", "Account provisioning timestamp"]
        ],
        ["id", "name", "email", "password_hash", "created_at"],
        [
            ["1", "Institute Administrator", "admin@hostelos.in", "$2b$12$d4EwX...", "2026-07-01 00:00:00"],
            ["2", "Dean of Student Affairs", "dean.hostels@hostelos.in", "$2b$12$k8LkP...", "2026-07-01 00:00:00"]
        ],
        col_w_dict=[1.4, 1.3, 2.2, 2.6],
        col_w_sample=[0.8, 2.4, 2.2, 1.2, 1.4]
    )

    # ==========================================
    # SECTION 5: NORMALIZATION PROOFS (1NF -> BCNF)
    # ==========================================
    add_h1("5. Normalization Theory & Formal BCNF Proofs")
    add_body(
        "A primary objective of 23CSE202 is eliminating data redundancies and update anomalies. "
        "Here is the formal proof showing HostelOS satisfies Boyce-Codd Normal Form (BCNF)."
    )

    add_h2("5.1 Flat Table Anomalies Eliminated")
    add_body("If we used a single unnormalized table FLAT_HOSTEL(roll_no, name, room_no, block, type_name, capacity, complaint_title, staff_name):", "The Naive Design: ")
    add_body("1. Insertion Anomaly: A new room type (e.g. '6-Bed Dorm') cannot be recorded unless an actual student occupies it.", "• ")
    add_body("2. Update Anomaly: Changing the capacity of 'Double AC' from 2 to 3 requires modifying thousands of rows. An interrupted update leaves the database corrupt.", "• ")
    add_body("3. Deletion Anomaly: Deleting the only student in Room 101 destroys the fact that Room 101 exists in Block A.", "• ")

    add_h2("5.2 Formal Normalization Progression")
    add_body("• First Normal Form (1NF): All attributes contain strictly atomic, scalar values. No repeating groups or comma-separated lists.")
    add_body("• Second Normal Form (2NF): In 1NF and no non-prime attribute is partially dependent on any candidate key. Because all 10 tables use single-column surrogate primary keys (id), partial dependency is mathematically impossible.")
    add_body("• Third Normal Form (3NF): In 2NF and no transitive functional dependencies exist. Decomposing ROOM and ROOM_TYPE eliminates the transitive dependency: id -> type_id -> capacity.")
    add_body("• Boyce-Codd Normal Form (BCNF): For every non-trivial functional dependency X -> Y, X must be a superkey.")

    add_callout(doc, "In all 10 tables of HostelOS, every functional determinant (e.g., id, roll_number, email, (block, room_number), (student_id, date)) is a verified Superkey. Hence, HostelOS is strictly in BCNF.", "MATHEMATICAL BCNF VERIFICATION")

    # ==========================================
    # SECTION 6: TRANSACTION MANAGEMENT & ACID
    # ==========================================
    add_h1("6. Transaction Management & ACID Properties")
    add_body("Room allocation requires strict ACID execution to eliminate concurrency bugs such as double booking:")
    
    add_code_block(doc, 
        "BEGIN TRANSACTION;\n"
        "  -- 1. Lock room row & verify capacity\n"
        "  SELECT rt.capacity, COUNT(a.id) AS occupied\n"
        "  FROM rooms r\n"
        "  JOIN room_types rt ON r.type_id = rt.id\n"
        "  LEFT JOIN allocations a ON r.id = a.room_id AND a.is_active = TRUE\n"
        "  WHERE r.id = 101\n"
        "  GROUP BY rt.capacity\n"
        "  FOR UPDATE; -- Row-Level Lock prevents concurrent race conditions\n"
        "\n"
        "  -- 2. If occupied < capacity, proceed with allocation\n"
        "  INSERT INTO allocations (student_id, room_id, allocation_date, deposit_paid, is_active)\n"
        "  VALUES (1, 101, CURRENT_DATE, 5000.00, TRUE);\n"
        "COMMIT;"
    )

    add_body("• Atomicity: If a network disconnection occurs mid-transaction, all intermediate inserts roll back completely.\n"
             "• Consistency: System invariants (occupied beds <= room capacity) are verified prior to commit.\n"
             "• Isolation: Row-level locking (SELECT ... FOR UPDATE) ensures two students clicking 'Reserve Bed' simultaneously are serialized.\n"
             "• Durability: Committed transactions are permanently logged to the Write-Ahead Log (WAL) on disk, surviving power cuts.")

    # ==========================================
    # SECTION 7: INDEXING STRATEGY (B-TREES)
    # ==========================================
    add_h1("7. Physical Storage & Indexing Strategy (B-Trees)")
    add_body("Without indexes, query filtering defaults to a Full Table Scan (O(N)). With B-Tree secondary indexes, lookups complete in O(log N) time.")

    t_idx = doc.add_table(rows=9, cols=3)
    headers_idx = ["Index Name", "Target Table & Column", "DBMS Performance Justification"]
    for j, h in enumerate(headers_idx):
        t_idx.cell(0, j).paragraphs[0].text = h
    
    idx_data = [
        ("idx_students_roll", "students(roll_number)", "Accelerates student lookup during admission and roll-call queries"),
        ("idx_students_email", "students(email)", "High-speed credential authentication during student login (0.2ms seek)"),
        ("idx_authorities_email", "authorities(email)", "Fast authentication for wardens and administrative staff"),
        ("idx_admins_email", "admins(email)", "Instant authentication for IT superusers"),
        ("idx_rooms_block", "rooms(block)", "Optimizes block-based room availability filtering in UI"),
        ("idx_allocations_active", "allocations(is_active)", "Filters current occupants vs historical records without scanning dead rows"),
        ("idx_complaints_status", "complaints(status)", "Enables wardens to instantly retrieve 'Open' tickets without scanning resolved"),
        ("idx_attendance_date", "attendance(date)", "Accelerates nightly roll-call reporting and absent student identification")
    ]
    for i, row in enumerate(idx_data):
        for j, val in enumerate(row):
            t_idx.cell(i+1, j).paragraphs[0].text = val
    style_table(t_idx, col_widths=[1.8, 1.8, 3.8])
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ==========================================
    # SECTION 8: ESSENTIAL SQL QUERIES
    # ==========================================
    add_h1("8. Essential SQL Queries & Analytical Reports")
    add_body("Examiners frequently test SQL proficiency during viva evaluations. Below are core queries implemented in HostelOS:")

    add_h2("8.1 Multi-Table Inner Join (Active Occupant Details)")
    add_code_block(doc,
        "SELECT s.roll_number, s.name, r.block, r.room_number, rt.type_name, a.allocation_date\n"
        "FROM allocations a\n"
        "JOIN students s ON a.student_id = s.id\n"
        "JOIN rooms r ON a.room_id = r.id\n"
        "JOIN room_types rt ON r.type_id = rt.id\n"
        "WHERE a.is_active = TRUE;"
    )

    add_h2("8.2 Group By & Having (Identify At-Capacity Rooms)")
    add_code_block(doc,
        "SELECT r.block, r.room_number, rt.capacity, COUNT(a.id) AS occupied\n"
        "FROM rooms r\n"
        "JOIN room_types rt ON r.type_id = rt.id\n"
        "JOIN allocations a ON r.id = a.room_id\n"
        "WHERE a.is_active = TRUE\n"
        "GROUP BY r.id, r.block, r.room_number, rt.capacity\n"
        "HAVING COUNT(a.id) >= rt.capacity;"
    )

    add_h2("8.3 Analytical Turnaround Time (Average Repair Time by Trade)")
    add_code_block(doc,
        "SELECT st.role_type AS trade, COUNT(c.id) AS tickets_resolved,\n"
        "       ROUND(AVG(EXTRACT(EPOCH FROM (c.resolved_at - c.created_at)) / 3600), 2) AS avg_hours\n"
        "FROM complaints c\n"
        "JOIN staff st ON c.staff_id = st.id\n"
        "WHERE c.status = 'Resolved' AND c.resolved_at IS NOT NULL\n"
        "GROUP BY st.role_type;"
    )

    # ==========================================
    # SECTION 9: TOP 20 VIVA QUESTIONS & MODEL ANSWERS
    # ==========================================
    add_h1("9. Top 20 DBMS Viva Questions & Model Answers")
    add_body("These questions represent the most commonly asked queries by university examiners for course 23CSE202:")

    viva_qas = [
        ("What is the primary objective of HostelOS?", 
         "HostelOS is a relational database management system designed to eliminate manual registers, prevent room overbooking through capacity validation, automate maintenance complaint ticketing, and provide idempotent attendance and digital gate passes."),
        ("What normal form is your database in?", 
         "Our schema is strictly in Boyce-Codd Normal Form (BCNF). Every determinant in all 10 tables is a superkey, eliminating all partial and transitive functional dependencies."),
        ("Why did you separate ROOM and ROOM_TYPE?", 
         "To eliminate transitive functional dependency. If capacity were stored inside ROOM, capacity would depend on type_name, which depends on room_id. Decomposing them into room_types satisfies 3NF and BCNF, preventing update anomalies when room capacities change."),
        ("Why is ALLOCATION a separate table instead of putting room_id inside STUDENT?", 
         "Storing room_id in STUDENT would only allow storing a student's current room, destroying historical residency records when students shift rooms across semesters. ALLOCATION acts as an associative junction entity resolving the M:N relationship over time."),
        ("What is the difference between a Candidate Key and a Primary Key?", 
         "A Candidate Key is any minimal superkey capable of uniquely identifying a row (e.g., roll_number and email in STUDENT). The Primary Key is the specific candidate key selected by the database designer to identify rows and anchor foreign keys. We chose surrogate id integers for performance."),
        ("What is a surrogate key, and why did you use it?", 
         "A surrogate key is an artificial, system-generated integer identifier (id SERIAL PRIMARY KEY) with no business meaning. Surrogate integer keys index faster in B-Trees, consume less storage than strings, and insulate foreign keys from changes in natural keys."),
        ("How does your database guarantee that a room is not overbooked?", 
         "During allocation transactions, the backend and database constraints compare room_types.capacity against the active rows (is_active = TRUE) in allocations. If active_count == capacity, the transaction rolls back with an error."),
        ("What does ON DELETE RESTRICT do on rooms.type_id?", 
         "It enforces referential integrity by preventing the deletion of a room category from room_types as long as any physical room in the rooms table still references it."),
        ("Why is staff_id in complaints nullable and set to ON DELETE SET NULL?", 
         "When a ticket is first created, no technician has been assigned yet, so staff_id must allow NULL. If a technician leaves the university, ON DELETE SET NULL ensures past complaint records and resolution histories are retained for auditing."),
        ("How do you prevent a student from being marked for attendance twice on the same night?", 
         "We enforce a composite unique constraint: CONSTRAINT uq_student_date UNIQUE (student_id, date). Any duplicate insertion attempt on the same calendar day throws a Unique Key Violation."),
        ("How do you validate that a student's leave return date is after their departure date?", 
         "Through a check constraint: CONSTRAINT chk_leave_dates CHECK (return_date >= departure_date). The database engine evaluates this predicate before committing any INSERT or UPDATE."),
        ("What is the difference between 3NF and BCNF?", 
         "In 3NF, for a dependency X -> Y, if X is not a superkey, the dependency is still permitted if Y is a prime attribute. BCNF removes this relaxation: X must be a superkey with no exceptions."),
        ("What index structure is used for your primary keys?", 
         "PostgreSQL and SQLite use B-Trees (Balanced Trees). B-Trees maintain sorted data in logarithmic time (O(log N)), providing fast searches, insertions, and range queries."),
        ("What is the difference between a Clustered and Non-Clustered Index?", 
         "A Clustered Index physically orders the data rows on disk according to the key (id PRIMARY KEY). A Non-Clustered (Secondary) Index creates a separate B-Tree containing pointers to physical rows (e.g. roll_number index)."),
        ("What is the difference between DDL, DML, and DQL?", 
         "DDL (Data Definition Language) defines schema structure (CREATE, ALTER, DROP). DML (Data Manipulation Language) modifies data (INSERT, UPDATE, DELETE). DQL (Data Query Language) retrieves data (SELECT)."),
        ("What is an associative junction table? Name one in your project.", 
         "An associative table decomposes an M:N relationship into two 1:N relationships by storing the foreign keys of both tables. In HostelOS, ALLOCATION is the associative table between STUDENT and ROOM."),
        ("What is an Insertion Anomaly? Give an example from your project.", 
         "An insertion anomaly occurs when certain attributes cannot be inserted without inserting unrelated attributes. For example, if room capacity were stored inside ROOM, we could not record a new room design until an actual physical room was constructed."),
        ("What is a Deletion Anomaly? Give an example from your project.", 
         "A deletion anomaly occurs when deleting certain data unintentionally deletes other unrelated data. For example, if room details were stored inside STUDENT, deleting the last graduating student from Room 204 would delete the record that Room 204 exists in Block A."),
        ("How do you handle concurrency during room booking?", 
         "We execute the allocation inside an ACID transaction with row-level locks (SELECT ... FOR UPDATE). If two students try to book the last available bed at the same instant, the database locks the room row, allowing the first transaction to complete and causing the second to fail gracefully."),
        ("How are passwords stored in your database?", 
         "Passwords are never stored in plaintext. They are encrypted using salted bcrypt cryptographic hashes (password_hash VARCHAR(255)). Salt prevents dictionary and rainbow table attacks, and the work factor slows down brute-force attempts.")
    ]

    for q_idx, (q, a) in enumerate(viva_qas):
        add_body(f"Q{q_idx+1}: {q}", bold_prefix=None)
        p_ans = doc.add_paragraph()
        p_ans.paragraph_format.space_before = Pt(1)
        p_ans.paragraph_format.space_after = Pt(4)
        r_pre = p_ans.add_run("Model Answer: ")
        r_pre.bold = True
        r_pre.font.color.rgb = BLUE
        r_ans = p_ans.add_run(a)
        r_ans.font.name = "Calibri"
        r_ans.font.size = Pt(9.5)

    # Save to both target locations
    output_filename1 = "HostelOS_Complete_DBMS_Documentation.docx"
    output_filename2 = "HostelOS_Database_Documentation.docx"
    
    doc.save(output_filename1)
    doc.save(output_filename2)
    print(f"Successfully generated {output_filename1} and {output_filename2}")

if __name__ == "__main__":
    create_document()
