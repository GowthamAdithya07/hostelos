"""
=============================================================================
HOSTELOS - 10-TABLE RELATIONAL DBMS QUERY EXECUTOR & VIVA VERIFICATION TOOL
=============================================================================
Course: 23CSE202 - Database Management Systems (Group C9)
Project: Hostel Room Allocation & Complaint Management System
Team:
  - Siddharth Sai   (AM.SC.U4CSE25209)
  - Gowtham Adithya (AM.SC.U4CSE25258)
  - Rama Sri Surya  (AM.SC.U4CSE25263)
  - Sai Santhosh    (AM.SC.U4CSE25264)

The 10 Relational Schema Tables Demonstrated:
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

Run this script to demonstrate core DBMS concepts live to your professor/evaluator:
  python database/test_dbms_queries.py
=============================================================================
"""

import sys
from pathlib import Path
from sqlalchemy import text
from fastapi.testclient import TestClient

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database import engine, SessionLocal
from app.main import app


def separator(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)


def run_demonstration():
    db = SessionLocal()
    try:
        # -------------------------------------------------------------
        # QUERY 1: Multi-Table Relational JOIN (4 Tables)
        # -------------------------------------------------------------
        separator("1. Multi-Table Relational JOIN (students + allocations + rooms + complaints + staff)")
        print("SQL: Fetch active complaints joined with Student, Room, and Assigned Staff Technician:")
        sql_join = """
            SELECT c.ticket_number, c.category, c.urgency, c.status,
                   s.name AS student_name, s.roll_number,
                   r.room_number, r.block,
                   COALESCE(st.name, 'Unassigned') AS staff_technician
            FROM complaints c
            JOIN students s ON c.student_id = s.id
            LEFT JOIN staff st ON c.staff_id = st.id
            LEFT JOIN allocations a ON a.student_id = s.id AND a.is_active = 1
            LEFT JOIN rooms r ON a.room_id = r.id
            WHERE c.status != 'Resolved'
            ORDER BY c.created_at DESC
            LIMIT 5;
        """
        print(sql_join.strip())
        print("-" * 80)
        rows = db.execute(text(sql_join)).fetchall()
        for r in rows:
            print(f"Ticket: {r[0]:<12} | Category: {r[1]:<20} | Urgency: {r[2]:<6} | Student: {r[4]} ({r[6]}, {r[7]}) | Tech: {r[8]}")

        # -------------------------------------------------------------
        # QUERY 2: Aggregations with GROUP BY & HAVING (Normalized RoomTypes)
        # -------------------------------------------------------------
        separator("2. Aggregation with GROUP BY & HAVING (Block Occupancy Rates across Normalized Tables)")
        print("SQL: Calculate total capacity, occupied beds, and vacancy per Block:")
        sql_group = """
            SELECT r.block,
                   COUNT(DISTINCT r.id) AS total_rooms,
                   SUM(rt.capacity) AS total_beds,
                   COUNT(a.id) AS occupied_beds,
                   (SUM(rt.capacity) - COUNT(a.id)) AS vacant_beds,
                   ROUND(CAST(COUNT(a.id) * 100.0 / NULLIF(SUM(rt.capacity), 0) AS NUMERIC), 1) AS occupancy_percentage
            FROM rooms r
            JOIN room_types rt ON r.type_id = rt.id
            LEFT JOIN allocations a ON a.room_id = r.id AND a.is_active = 1
            GROUP BY r.block
            HAVING SUM(rt.capacity) > 0
            ORDER BY r.block ASC;
        """
        print(sql_group.strip())
        print("-" * 80)
        rows = db.execute(text(sql_group)).fetchall()
        for r in rows:
            print(f"Block: {r[0]:<10} | Rooms: {r[1]:<2} | Total Beds: {r[2]:<2} | Occupied: {r[3]:<2} | Vacant: {r[4]:<2} | Occupancy: {r[5]}%")

        # -------------------------------------------------------------
        # QUERY 3: Pattern Matching (LIKE on Student Roll Numbers)
        # -------------------------------------------------------------
        separator("3. Pattern Search (LIKE pattern matching on Student Roster)")
        print("SQL: Search students matching 'AM.SC.U4CSE252%' enrolled in Computer Science:")
        sql_like = """
            SELECT s.roll_number, s.name, s.emergency_contact, r.room_number, r.block
            FROM students s
            LEFT JOIN allocations a ON a.student_id = s.id AND a.is_active = 1
            LEFT JOIN rooms r ON a.room_id = r.id
            WHERE s.roll_number LIKE 'AM.SC.U4CSE252%'
            ORDER BY s.roll_number ASC
            LIMIT 5;
        """
        print(sql_like.strip())
        print("-" * 80)
        rows = db.execute(text(sql_like)).fetchall()
        for r in rows:
            print(f"Roll: {r[0]:<16} | Name: {r[1]:<20} | Room: {r[3] or 'N/A'} ({r[4] or 'N/A'}) | Contact: {r[2]}")

        # -------------------------------------------------------------
        # QUERY 4: Subquery / Nested Query
        # -------------------------------------------------------------
        separator("4. Nested Subquery (Students who filed HIGH urgency complaints)")
        print("SQL: Subquery finding residents with open high-urgency maintenance tickets:")
        sql_sub = """
            SELECT s.name, s.email, s.roll_number, r.room_number
            FROM students s
            LEFT JOIN allocations a ON a.student_id = s.id AND a.is_active = 1
            LEFT JOIN rooms r ON a.room_id = r.id
            WHERE s.id IN (
                SELECT DISTINCT c.student_id
                FROM complaints c
                WHERE c.urgency = 'High' AND c.status = 'Open'
            );
        """
        print(sql_sub.strip())
        print("-" * 80)
        rows = db.execute(text(sql_sub)).fetchall()
        for r in rows:
            print(f"Student: {r[0]:<20} | Roll: {r[2]:<16} | Room: {r[3] or 'N/A':<6} | Email: {r[1]}")

        # -------------------------------------------------------------
        # QUERY 5: Attendance Roster Roll-Call Aggregation
        # -------------------------------------------------------------
        separator("5. Attendance Roster (Daily Night Roll-Call Breakdown)")
        print("SQL: Daily attendance breakdown:")
        sql_att = """
            SELECT a.date, a.status, COUNT(*) as count
            FROM attendance a
            GROUP BY a.date, a.status
            ORDER BY a.date DESC;
        """
        print(sql_att.strip())
        print("-" * 80)
        rows = db.execute(text(sql_att)).fetchall()
        for r in rows:
            print(f"Date: {r[0]} | Status: {r[1]:<16} | Student Count: {r[2]}")

        # -------------------------------------------------------------
        # QUERY 6: REST API Authentication & Role Linking Verification
        # -------------------------------------------------------------
        separator("6. REST API Role-Based Authentication & Table Verification")
        client = TestClient(app)

        # 1. Admin login
        r_admin = client.post("/auth/login", json={"email": "admin@hostelos.in", "password": "Admin@123"})
        print(f"[AUTH TEST] Admin Login: HTTP {r_admin.status_code} | Role: {r_admin.json()['user']['role']} (Table: admins)")
        assert r_admin.status_code == 200

        # 2. Warden login
        r_warden = client.post("/auth/login", json={"email": "warden@hostelos.in", "password": "Warden@123"})
        print(f"[AUTH TEST] Warden Login: HTTP {r_warden.status_code} | Role: {r_warden.json()['user']['role']} (Table: authorities)")
        assert r_warden.status_code == 200

        # 3. Student login
        r_student = client.post("/auth/login", json={"email": "siddharth@hostelos.in", "password": "Student@123"})
        student_data = r_student.json()["user"]
        print(f"[AUTH TEST] Student Login: HTTP {r_student.status_code} | Role: {student_data['role']} | Roll: {student_data['roll_number']} | Room: {student_data['room_number']} (Table: students)")
        assert r_student.status_code == 200

        # 4. Overview metrics
        r_metrics = client.get("/analytics/overview")
        m = r_metrics.json()
        print(f"[METRICS TEST] Capacity: {m['filled_beds']}/{m['total_beds']} ({m['occupancy_pct']}%) | Active Complaints: {m['active_complaints']} | Pending Passes: {m['pending_leaves']}")

        separator("ALL 10-TABLE RELATIONAL DBMS TESTS & AUTH VERIFICATIONS PASSED")

    except Exception as e:
        print(f"\n[QUERY ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run_demonstration()
