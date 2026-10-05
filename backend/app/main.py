"""
=============================================================================
HOSTELOS - 10-TABLE RELATIONAL DATABASE APPLICATION SERVER (FastAPI)
=============================================================================
Academic DBMS Reference Implementation:
  Group: C9 · Course: 23CSE202 (Database Management Systems)
  Application: Hostel Room Allocation and Complaint Management System

The 10 Relational Tables (BCNF / 3NF):
  1. STUDENT    (students)
  2. ROOM_TYPE  (room_types)
  3. ROOM       (rooms)
  4. ALLOCATION (allocations)
  5. ADMIN      (admins)
  6. STAFF      (staff)
  7. AUTHORITY  (authorities)
  8. COMPLAINT  (complaints)
  9. ATTENDANCE (attendance)
 10. LEAVE_PASS (leave_passes)

Authentic Credentials:
  - Institute Head: admin@hostelos.in / Admin@123 (table `admins`)
  - Chief Warden:   warden@hostelos.in / Warden@123 (table `authorities`)
  - Student:        siddharth@hostelos.in / Student@123 (table `students`)
=============================================================================
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from .database import engine, Base, SessionLocal
from .models import (
    Student,
    RoomType,
    Room,
    Allocation,
    Admin,
    Staff,
    Authority,
    Complaint,
    ComplaintCategory,
    ComplaintUrgency,
    ComplaintStatus,
    LeavePass,
    LeaveType,
    LeaveStatus,
    Attendance,
    AttendanceStatus,
    UserRole,
)
from .auth import get_password_hash
from .routers import auth, rooms, complaints, leaves, attendance, analytics

# Environment & Storage directories
BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BACKEND_DIR / ".env")

UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# SEED DATABASE ENGINE & INTEGRATION (10-TABLE DATASET)
# =============================================================================

def seed_hostelos_database():
    """
    Seeds initial relational records to populate all 10 tables:
      - Table 1: students (42 resident students)
      - Table 2: room_types (Single AC, Double AC, Single Non-AC, Double Non-AC)
      - Table 3: rooms (30 rooms = 54 beds across Blocks A, B, C)
      - Table 4: allocations (42 active assignments = 78% occupancy)
      - Table 5: admins (Prof. K. R. Ramanathan, Institute Head)
      - Table 6: staff (Murugan, Ramesh, Chandran, Velu)
      - Table 7: authorities (Dr. Suresh Kumar, Chief Warden)
      - Table 8: complaints (10 active + 1 resolved tickets)
      - Table 9: attendance (today's roll call: 90% Present benchmark)
      - Table 10: leave_passes (7 gate passes: 4 Pending)
    """
    db = SessionLocal()
    try:
        # Create all schema tables
        Base.metadata.create_all(bind=engine)

        # -------------------------------------------------------------
        # 1. TABLE: room_types (Table 2 of 10)
        # -------------------------------------------------------------
        if db.query(RoomType).count() == 0:
            type_double_ac = RoomType(type_name="Double AC", capacity=2)
            type_single_ac = RoomType(type_name="Single AC", capacity=1)
            type_double_non_ac = RoomType(type_name="Double Non-AC", capacity=2)
            type_single_non_ac = RoomType(type_name="Single Non-AC", capacity=1)
            db.add_all([type_double_ac, type_single_ac, type_double_non_ac, type_single_non_ac])
            db.commit()
            print("[DBMS Seed] Created 4 Room Types (Single AC, Double AC, Single Non-AC, Double Non-AC)")

        types_map = {rt.type_name: rt for rt in db.query(RoomType).all()}
        t_dac = types_map.get("Double AC")
        t_sac = types_map.get("Single AC")
        t_dnac = types_map.get("Double Non-AC")
        t_snac = types_map.get("Single Non-AC")

        # -------------------------------------------------------------
        # 2. TABLE: rooms (Table 3 of 10 - 54 Beds: Blocks A, B, C)
        # -------------------------------------------------------------
        if db.query(Room).count() == 0:
            rooms_to_create = [
                # Block A (Double AC / Single AC / Double Non-AC)
                Room(room_number="A-101", block="Block A", type_id=t_dac.id, has_ac=True),
                Room(room_number="A-102", block="Block A", type_id=t_dac.id, has_ac=True),
                Room(room_number="A-103", block="Block A", type_id=t_sac.id, has_ac=True),
                Room(room_number="A-104", block="Block A", type_id=t_dnac.id, has_ac=False),
                Room(room_number="A-201", block="Block A", type_id=t_dac.id, has_ac=True),
                Room(room_number="A-202", block="Block A", type_id=t_dnac.id, has_ac=False),
                Room(room_number="A-203", block="Block A", type_id=t_snac.id, has_ac=False),
                Room(room_number="A-204", block="Block A", type_id=t_dac.id, has_ac=True),
                Room(room_number="A-301", block="Block A", type_id=t_dac.id, has_ac=True),
                Room(room_number="A-302", block="Block A", type_id=t_dnac.id, has_ac=False),

                # Block B
                Room(room_number="B-101", block="Block B", type_id=t_dac.id, has_ac=True),
                Room(room_number="B-102", block="Block B", type_id=t_dac.id, has_ac=True),
                Room(room_number="B-103", block="Block B", type_id=t_sac.id, has_ac=True),
                Room(room_number="B-104", block="Block B", type_id=t_dnac.id, has_ac=False),
                Room(room_number="B-201", block="Block B", type_id=t_dnac.id, has_ac=False),
                Room(room_number="B-202", block="Block B", type_id=t_dac.id, has_ac=True),
                Room(room_number="B-203", block="Block B", type_id=t_snac.id, has_ac=False),
                Room(room_number="B-204", block="Block B", type_id=t_dnac.id, has_ac=False),
                Room(room_number="B-301", block="Block B", type_id=t_dac.id, has_ac=True),
                Room(room_number="B-302", block="Block B", type_id=t_dnac.id, has_ac=False),

                # Block C
                Room(room_number="C-101", block="Block C", type_id=t_dnac.id, has_ac=False),
                Room(room_number="C-102", block="Block C", type_id=t_dnac.id, has_ac=False),
                Room(room_number="C-103", block="Block C", type_id=t_snac.id, has_ac=False),
                Room(room_number="C-104", block="Block C", type_id=t_dnac.id, has_ac=False),
                Room(room_number="C-201", block="Block C", type_id=t_dnac.id, has_ac=False),
                Room(room_number="C-202", block="Block C", type_id=t_dnac.id, has_ac=False),
                Room(room_number="C-203", block="Block C", type_id=t_snac.id, has_ac=False),
                Room(room_number="C-204", block="Block C", type_id=t_dnac.id, has_ac=False),
                Room(room_number="C-205", block="Block C", type_id=t_dnac.id, has_ac=False),
                Room(room_number="C-206", block="Block C", type_id=t_dnac.id, has_ac=False),
            ]
            db.add_all(rooms_to_create)
            db.commit()
            print("[DBMS Seed] Created 30 Rooms across Blocks A, B, and C (54 beds total)")

        rooms_dict = {r.room_number: r for r in db.query(Room).all()}

        # -------------------------------------------------------------
        # 3. TABLE: admins (Table 5 of 10)
        # -------------------------------------------------------------
        admin_email = "admin@hostelos.in"
        admin = db.query(Admin).filter(Admin.email == admin_email).first()
        if not admin:
            admin = Admin(
                name="Prof. K. R. Ramanathan",
                email=admin_email,
                password_hash=get_password_hash("Admin@123"),
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("[DBMS Seed] Created Admin: Prof. K. R. Ramanathan (admin@hostelos.in)")

        # -------------------------------------------------------------
        # 4. TABLE: authorities (Table 7 of 10 - Wardens)
        # -------------------------------------------------------------
        warden_email = "warden@hostelos.in"
        warden = db.query(Authority).filter(Authority.email == warden_email).first()
        if not warden:
            warden = Authority(
                name="Dr. Suresh Kumar",
                designation="Chief Warden",
                email=warden_email,
                password_hash=get_password_hash("Warden@123"),
            )
            db.add(warden)
            db.commit()
            db.refresh(warden)
            print("[DBMS Seed] Created Authority: Dr. Suresh Kumar (warden@hostelos.in)")

        # -------------------------------------------------------------
        # 5. TABLE: staff (Table 6 of 10 - Technicians)
        # -------------------------------------------------------------
        if db.query(Staff).count() == 0:
            staff_list = [
                Staff(name="Murugan", role_type="Senior Electrician", phone="+91 98401 23456"),
                Staff(name="Ramesh", role_type="Plumber", phone="+91 98402 34567"),
                Staff(name="Chandran", role_type="Carpenter", phone="+91 98403 45678"),
                Staff(name="Velu", role_type="Housekeeping", phone="+91 98404 56789"),
            ]
            db.add_all(staff_list)
            db.commit()
            print("[DBMS Seed] Created 4 Staff Technicians (Electrician, Plumber, Carpenter, Housekeeping)")

        staff_map = {s.name: s for s in db.query(Staff).all()}

        # -------------------------------------------------------------
        # 6. TABLE: students (Table 1 of 10 - 42 Students)
        # -------------------------------------------------------------
        students_roster = [
            ("Siddharth Verma", "siddharth@hostelos.in", "AM.SC.U4CSE25209", "+91 98765 43210", "A-101"),
            ("Aarav Sharma", "aarav@hostelos.in", "AM.SC.U4CSE25001", "+91 98111 22334", "A-101"),
            ("Rohan Iyer", "rohan@hostelos.in", "AM.SC.U4CSE25045", "+91 97222 33445", "A-102"),
            ("Kavya Krishnan", "kavya@hostelos.in", "AM.SC.U4CSE25088", "+91 96333 44556", "A-102"),
            ("Vikram Malhotra", "vikram@hostelos.in", "AM.SC.U4CSE25112", "+91 95444 55667", "A-103"),
            ("Ananya Roy", "ananya@hostelos.in", "AM.SC.U4CSE25189", "+91 94555 66778", "A-104"),
            ("Tanvi Sen", "tanvi@hostelos.in", "AM.SC.U4CSE25190", "+91 93666 77889", "A-104"),
            ("Aditya Nair", "aditya@hostelos.in", "AM.SC.U4CSE25210", "+91 92777 88990", "A-201"),
            ("Karthik Rao", "karthik@hostelos.in", "AM.SC.U4CSE25215", "+91 91888 99001", "A-201"),
            ("Neha Nambiar", "neha@hostelos.in", "AM.SC.U4CSE25230", "+91 90999 00112", "A-202"),
            ("Pooja Hegde", "pooja@hostelos.in", "AM.SC.U4CSE25231", "+91 99000 11223", "A-202"),
            ("Rahul Menon", "rahul@hostelos.in", "AM.SC.U4CSE25240", "+91 98123 45678", "A-203"),
            ("Manish Pandey", "manish@hostelos.in", "AM.SC.U4CSE25255", "+91 97234 56789", "A-204"),
            ("Gautam Gambhir", "gautam@hostelos.in", "AM.SC.U4CSE25256", "+91 96345 67890", "A-204"),
            ("Harsh Vardhan", "harsh@hostelos.in", "AM.SC.U4CSE25260", "+91 95456 78901", "A-301"),
            ("Devendra Singh", "devendra@hostelos.in", "AM.SC.U4CSE25261", "+91 94567 89012", "A-301"),
            ("Yashwanth Reddy", "yash@hostelos.in", "AM.SC.U4CSE25270", "+91 93678 90123", "A-302"),
            ("Varun Tej", "varun@hostelos.in", "AM.SC.U4CSE25271", "+91 92789 01234", "A-302"),

            # Block B Residents
            ("Deepak Chahar", "deepak@hostelos.in", "AM.SC.U4CSE25280", "+91 91890 12345", "B-101"),
            ("Shubman Gill", "shubman@hostelos.in", "AM.SC.U4CSE25281", "+91 90901 23456", "B-101"),
            ("Hardik Pandya", "hardik@hostelos.in", "AM.SC.U4CSE25290", "+91 99012 34567", "B-102"),
            ("Krunal Pandya", "krunal@hostelos.in", "AM.SC.U4CSE25291", "+91 98123 45679", "B-102"),
            ("Ravindra Jadeja", "ravindra@hostelos.in", "AM.SC.U4CSE25300", "+91 97234 56780", "B-103"),
            ("Suryakumar Yadav", "surya@hostelos.in", "AM.SC.U4CSE25310", "+91 96345 67891", "B-104"),
            ("Tilak Varma", "tilak@hostelos.in", "AM.SC.U4CSE25311", "+91 95456 78902", "B-104"),
            ("Jasprit Bumrah", "jasprit@hostelos.in", "AM.SC.U4CSE25320", "+91 94567 89013", "B-201"),
            ("Mohammed Siraj", "siraj@hostelos.in", "AM.SC.U4CSE25321", "+91 93678 90124", "B-201"),
            ("Kuldeep Yadav", "kuldeep@hostelos.in", "AM.SC.U4CSE25330", "+91 92789 01235", "B-202"),
            ("Yuzvendra Chahal", "chahal@hostelos.in", "AM.SC.U4CSE25331", "+91 91890 12346", "B-202"),
            ("Axar Patel", "axar@hostelos.in", "AM.SC.U4CSE25340", "+91 90901 23457", "B-203"),
            ("Washington Sundar", "sundar@hostelos.in", "AM.SC.U4CSE25350", "+91 99012 34568", "B-204"),
            ("Ravi Bishnoi", "bishnoi@hostelos.in", "AM.SC.U4CSE25351", "+91 98123 45680", "B-204"),
            ("Arshdeep Singh", "arshdeep@hostelos.in", "AM.SC.U4CSE25360", "+91 97234 56781", "B-301"),
            ("Avesh Khan", "avesh@hostelos.in", "AM.SC.U4CSE25361", "+91 96345 67892", "B-301"),
            ("Mukesh Kumar", "mukesh@hostelos.in", "AM.SC.U4CSE25370", "+91 95456 78903", "B-302"),

            # Block C Residents
            ("Sanju Samson", "sanju@hostelos.in", "AM.SC.U4CSE25380", "+91 94567 89014", "C-101"),
            ("Rinku Singh", "rinku@hostelos.in", "AM.SC.U4CSE25381", "+91 93678 90125", "C-101"),
            ("Jitesh Sharma", "jitesh@hostelos.in", "AM.SC.U4CSE25390", "+91 92789 01236", "C-102"),
            ("Shivam Dube", "shivam@hostelos.in", "AM.SC.U4CSE25391", "+91 91890 12347", "C-102"),
            ("Dhruv Jurel", "dhruv@hostelos.in", "AM.SC.U4CSE25400", "+91 90901 23458", "C-103"),
            ("Prasidh Krishna", "prasidh@hostelos.in", "AM.SC.U4CSE25410", "+91 99012 34569", "C-104"),
            ("Sai Sudharsan", "sai@hostelos.in", "AM.SC.U4CSE25411", "+91 98123 45681", "C-104"),
        ]

        created_students = {}
        for name, email, roll, phone, r_num in students_roster:
            s_exist = db.query(Student).filter(Student.email == email).first()
            if not s_exist:
                s_obj = Student(
                    name=name,
                    email=email,
                    password_hash=get_password_hash("Student@123"),
                    roll_number=roll,
                    emergency_contact=phone,
                    major="Computer Science & Engineering",
                )
                db.add(s_obj)
                db.commit()
                db.refresh(s_obj)
                created_students[email] = s_obj
            else:
                created_students[email] = s_exist

        # -------------------------------------------------------------
        # 7. TABLE: allocations (Table 4 of 10 - Bed Assignments)
        # -------------------------------------------------------------
        if db.query(Allocation).count() == 0:
            alloc_records = []
            for name, email, roll, phone, r_num in students_roster:
                student = created_students.get(email)
                room = rooms_dict.get(r_num)
                if student and room:
                    alloc_records.append(
                        Allocation(
                            student_id=student.id,
                            room_id=room.id,
                            allocation_date=date.today() - timedelta(days=60),
                            deposit_paid=5000.00,
                            is_active=True,
                        )
                    )
            db.add_all(alloc_records)
            db.commit()
            print(f"[DBMS Seed] Created {len(alloc_records)} Allocations (42/54 Beds = 78% Occupancy)")

        # -------------------------------------------------------------
        # 8. TABLE: complaints (Table 8 of 10 - 10 Active Complaints)
        # -------------------------------------------------------------
        if db.query(Complaint).count() == 0:
            siddharth = created_students.get("siddharth@hostelos.in")
            aarav = created_students.get("aarav@hostelos.in")
            rohan = created_students.get("rohan@hostelos.in")
            vikram = created_students.get("vikram@hostelos.in")
            ananya = created_students.get("ananya@hostelos.in")
            aditya = created_students.get("aditya@hostelos.in")

            complaints_data = [
                Complaint(
                    ticket_number="CM-2026-0230",
                    student_id=siddharth.id if siddharth else 1,
                    staff_id=staff_map.get("Ramesh", None).id if staff_map.get("Ramesh") else None,
                    category=ComplaintCategory.PLUMBING.value,
                    title="Bathroom tap leaking continuously",
                    description="The main washbasin tap in room A-101 is dripping heavily, causing water pooling on the floor.",
                    urgency=ComplaintUrgency.HIGH.value,
                    status=ComplaintStatus.OPEN.value,
                    assigned_staff="Ramesh (Plumber)",
                ),
                Complaint(
                    ticket_number="CM-2026-0229",
                    student_id=aarav.id if aarav else 1,
                    staff_id=staff_map.get("Murugan", None).id if staff_map.get("Murugan") else None,
                    category=ComplaintCategory.ELECTRICAL.value,
                    title="Ceiling fan speed regulator burnt",
                    description="Regulator switch emitted smoke and fan is stuck on full speed without speed control.",
                    urgency=ComplaintUrgency.HIGH.value,
                    status=ComplaintStatus.ESCALATED.value,
                    assigned_staff="Murugan (Senior Electrician)",
                ),
                Complaint(
                    ticket_number="CM-2026-0228",
                    student_id=rohan.id if rohan else 1,
                    staff_id=staff_map.get("Murugan", None).id if staff_map.get("Murugan") else None,
                    category=ComplaintCategory.INTERNET.value,
                    title="WiFi router in corridor dropped packets",
                    description="Frequent disconnection and high latency (90% packet loss) on 5GHz band.",
                    urgency=ComplaintUrgency.MEDIUM.value,
                    status=ComplaintStatus.OPEN.value,
                    assigned_staff="Murugan (Senior Electrician)",
                ),
                Complaint(
                    ticket_number="CM-2026-0227",
                    student_id=vikram.id if vikram else 1,
                    staff_id=staff_map.get("Chandran", None).id if staff_map.get("Chandran") else None,
                    category=ComplaintCategory.FURNITURE.value,
                    title="Study table drawer lock broken",
                    description="Key broken inside lock cylinder, cannot access study material.",
                    urgency=ComplaintUrgency.LOW.value,
                    status=ComplaintStatus.OPEN.value,
                    assigned_staff="Chandran (Carpenter)",
                ),
                Complaint(
                    ticket_number="CM-2026-0226",
                    student_id=ananya.id if ananya else 1,
                    staff_id=staff_map.get("Ramesh", None).id if staff_map.get("Ramesh") else None,
                    category=ComplaintCategory.PLUMBING.value,
                    title="Water purifier filter beeping red",
                    description="Floor 1 water dispenser shows filter change error code and shuts down.",
                    urgency=ComplaintUrgency.HIGH.value,
                    status=ComplaintStatus.ESCALATED.value,
                    assigned_staff="Ramesh (Plumber)",
                ),
                Complaint(
                    ticket_number="CM-2026-0225",
                    student_id=aditya.id if aditya else 1,
                    staff_id=staff_map.get("Velu", None).id if staff_map.get("Velu") else None,
                    category=ComplaintCategory.HOUSEKEEPING.value,
                    title="Window pane cracked after heavy rain",
                    description="Outer glass panel has stress crack, risk of water seepage.",
                    urgency=ComplaintUrgency.MEDIUM.value,
                    status=ComplaintStatus.OPEN.value,
                    assigned_staff="Velu (Housekeeping)",
                ),
                Complaint(
                    ticket_number="CM-2026-0224",
                    student_id=siddharth.id if siddharth else 1,
                    staff_id=staff_map.get("Murugan", None).id if staff_map.get("Murugan") else None,
                    category=ComplaintCategory.ELECTRICAL.value,
                    title="Switchboard sparking upon plug insertion",
                    description="Wall socket in desk area produces sparks when laptop adapter is inserted.",
                    urgency=ComplaintUrgency.HIGH.value,
                    status=ComplaintStatus.OPEN.value,
                    assigned_staff="Murugan (Senior Electrician)",
                ),
                Complaint(
                    ticket_number="CM-2026-0223",
                    student_id=aarav.id if aarav else 1,
                    staff_id=staff_map.get("Murugan", None).id if staff_map.get("Murugan") else None,
                    category=ComplaintCategory.ELECTRICAL.value,
                    title="AC condenser rattling violently",
                    description="Outdoor unit vibrates and makes grinding noise when cooling engages.",
                    urgency=ComplaintUrgency.MEDIUM.value,
                    status=ComplaintStatus.OPEN.value,
                    assigned_staff="Murugan (Senior Electrician)",
                ),
                Complaint(
                    ticket_number="CM-2026-0222",
                    student_id=rohan.id if rohan else 1,
                    staff_id=staff_map.get("Murugan", None).id if staff_map.get("Murugan") else None,
                    category=ComplaintCategory.ELECTRICAL.value,
                    title="Corridor lighting tubes flickering",
                    description="East corridor tube light keeps blinking causing headache.",
                    urgency=ComplaintUrgency.LOW.value,
                    status=ComplaintStatus.OPEN.value,
                    assigned_staff="Murugan (Senior Electrician)",
                ),
                Complaint(
                    ticket_number="CM-2026-0221",
                    student_id=vikram.id if vikram else 1,
                    staff_id=staff_map.get("Ramesh", None).id if staff_map.get("Ramesh") else None,
                    category=ComplaintCategory.PLUMBING.value,
                    title="Washroom drainage overflow",
                    description="Floor drain water backing up during peak morning hours.",
                    urgency=ComplaintUrgency.HIGH.value,
                    status=ComplaintStatus.OPEN.value,
                    assigned_staff="Ramesh (Plumber)",
                ),
                # Resolved complaint
                Complaint(
                    ticket_number="CM-2026-0219",
                    student_id=siddharth.id if siddharth else 1,
                    staff_id=staff_map.get("Murugan", None).id if staff_map.get("Murugan") else None,
                    category=ComplaintCategory.ELECTRICAL.value,
                    title="Tube light replacement in study desk",
                    description="Desk lamp tube burned out.",
                    urgency=ComplaintUrgency.LOW.value,
                    status=ComplaintStatus.RESOLVED.value,
                    assigned_staff="Murugan (Senior Electrician)",
                    resolution_notes="Replaced with new 18W Philips LED tube.",
                    resolved_at=datetime.now(timezone.utc),
                ),
            ]
            db.add_all(complaints_data)
            db.commit()
            print("[DBMS Seed] Created 11 Complaints (10 Active matching Dashboard KPI)")

        # -------------------------------------------------------------
        # 9. TABLE: leave_passes (Table 10 of 10 - 7 Passes: 4 Pending)
        # -------------------------------------------------------------
        if db.query(LeavePass).count() == 0:
            now = datetime.now(timezone.utc)
            leaves_data = [
                LeavePass(
                    pass_code="GP-2026-4417",
                    student_id=created_students["aarav@hostelos.in"].id,
                    authority_id=warden.id,
                    leave_type=LeaveType.WEEKEND.value,
                    depart_expected=now,
                    expected_return=now + timedelta(days=2),
                    destination="Bangalore, Karnataka",
                    reason="Attending family function over weekend.",
                    emergency_contact="+91 98451 99887",
                    parent_consent=True,
                    status=LeaveStatus.APPROVED.value,
                    gate_pass_token="HOSTEL-PASS-AUTH-4417-7721",
                ),
                LeavePass(
                    pass_code="GP-2026-4416",
                    student_id=created_students["siddharth@hostelos.in"].id,
                    authority_id=warden.id,
                    leave_type=LeaveType.VACATION.value,
                    depart_expected=now + timedelta(days=1),
                    expected_return=now + timedelta(days=5),
                    destination="Chennai, Tamil Nadu",
                    reason="Semester break visit back home.",
                    emergency_contact="+91 94440 12345",
                    parent_consent=True,
                    status=LeaveStatus.VALIDATED.value,
                    gate_pass_token="HOSTEL-PASS-AUTH-4416-8812",
                ),
                LeavePass(
                    pass_code="GP-2026-4415",
                    student_id=created_students["rohan@hostelos.in"].id,
                    authority_id=warden.id,
                    leave_type=LeaveType.WEEKEND.value,
                    depart_expected=now + timedelta(hours=3),
                    expected_return=now + timedelta(days=2),
                    destination="Mysore, Karnataka",
                    reason="Visiting native place.",
                    emergency_contact="+91 97400 33221",
                    parent_consent=True,
                    status=LeaveStatus.APPROVED.value,
                    gate_pass_token="HOSTEL-PASS-AUTH-4415-3390",
                ),
                # 4 Pending leaves matching Dashboard KPI
                LeavePass(
                    pass_code="GP-2026-4414",
                    student_id=created_students["vikram@hostelos.in"].id,
                    authority_id=None,
                    leave_type=LeaveType.EMERGENCY.value,
                    depart_expected=now + timedelta(hours=1),
                    expected_return=now + timedelta(days=3),
                    destination="Coimbatore, Tamil Nadu",
                    reason="Medical emergency at home.",
                    emergency_contact="+91 95444 88776",
                    parent_consent=True,
                    status=LeaveStatus.PENDING.value,
                ),
                LeavePass(
                    pass_code="GP-2026-4413",
                    student_id=created_students["ananya@hostelos.in"].id,
                    authority_id=None,
                    leave_type=LeaveType.WEEKEND.value,
                    depart_expected=now + timedelta(days=1),
                    expected_return=now + timedelta(days=3),
                    destination="Kochi, Kerala",
                    reason="Brother's wedding reception.",
                    emergency_contact="+91 94471 22334",
                    parent_consent=True,
                    status=LeaveStatus.PENDING.value,
                ),
                LeavePass(
                    pass_code="GP-2026-4412",
                    student_id=created_students["aditya@hostelos.in"].id,
                    authority_id=None,
                    leave_type=LeaveType.VACATION.value,
                    depart_expected=now + timedelta(days=2),
                    expected_return=now + timedelta(days=7),
                    destination="Trivandrum, Kerala",
                    reason="Annual family gathering.",
                    emergency_contact="+91 94470 55443",
                    parent_consent=True,
                    status=LeaveStatus.PENDING.value,
                ),
                LeavePass(
                    pass_code="GP-2026-4411",
                    student_id=created_students["karthik@hostelos.in"].id,
                    authority_id=None,
                    leave_type=LeaveType.WEEKEND.value,
                    depart_expected=now + timedelta(days=1),
                    expected_return=now + timedelta(days=2),
                    destination="Bangalore, Karnataka",
                    reason="Attending tech symposium at IISc.",
                    emergency_contact="+91 98450 66778",
                    parent_consent=True,
                    status=LeaveStatus.PENDING.value,
                ),
            ]
            db.add_all(leaves_data)
            db.commit()
            print("[DBMS Seed] Created 7 Gate Passes (4 Pending matching Dashboard KPI)")

        # -------------------------------------------------------------
        # 10. TABLE: attendance (Table 9 of 10 - 90% Present benchmark)
        # -------------------------------------------------------------
        today = date.today()
        if db.query(Attendance).filter(Attendance.date == today).count() == 0:
            attendance_records = []
            all_students = db.query(Student).all()
            for idx, stu in enumerate(all_students):
                # 90% Present, 10% Late/Permitted or Absent
                if idx in [4, 14]:
                    status_val = AttendanceStatus.ABSENT.value
                    notes = "On emergency leave"
                elif idx in [8, 19]:
                    status_val = AttendanceStatus.LATE.value
                    notes = "Late lab checkout permitted by HOD"
                else:
                    status_val = AttendanceStatus.PRESENT.value
                    notes = None

                attendance_records.append(
                    Attendance(
                        student_id=stu.id,
                        admin_id=admin.id,
                        date=today,
                        status=status_val,
                        notes=notes,
                    )
                )
            db.add_all(attendance_records)
            db.commit()
            print(f"[DBMS Seed] Created {len(attendance_records)} Attendance records for {today} (90% Present)")

    except Exception as e:
        db.rollback()
        print(f"[DBMS Seed ERROR] {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application Startup & Shutdown lifecycle hooks."""
    print("[HostelOS] Starting Relational Database Backend...")
    seed_hostelos_database()
    yield
    print("[HostelOS] Shutting down application cleanly.")


# =============================================================================
# FASTAPI APPLICATION INSTANCE
# =============================================================================

app = FastAPI(
    title="HostelOS - Relational DBMS API",
    description="Backend API for Hostel Room Allocation & Complaint Management System (23CSE202 DBMS Project Group C9)",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS Configuration: allows Vite dev server and local network testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads (attachments, photos)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include Modular API Routers
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(complaints.router)
app.include_router(leaves.router)
app.include_router(attendance.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "project": "HostelOS",
        "title": "Hostel Room Allocation & Complaint Management System",
        "group": "Group C9 · 23CSE202 (Database Management Systems)",
        "status": "Operational",
        "docs_url": "/docs",
    }
