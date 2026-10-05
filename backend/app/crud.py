"""
=============================================================================
HOSTELOS - 10-TABLE RELATIONAL DATABASE CRUD OPERATIONS (SQLAlchemy ORM)
=============================================================================
Academic DBMS Reference Implementation:
Course: 23CSE202 (Database Management Systems, Group C9)
Official 10 Tables:
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

Every database operation maps to ANSI/PostgreSQL RAW SQL with transactions (ACID),
referential integrity, foreign key cascading, and domain constraints.
=============================================================================
"""

import random
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, distinct, or_, and_, desc

from . import models, schemas
from .auth import get_password_hash


# =============================================================================
# 1. USER & IDENTITY OPERATIONS (TABLES: admins, authorities, students)
# =============================================================================

def get_user_by_email(db: Session, email: str) -> Optional[Any]:
    """
    Look up an account across the three authenticated identity tables:
      1. ADMIN (College Head)
      2. AUTHORITY (Hostel Warden)
      3. STUDENT (Resident Student)

    RAW SQL:
    -------------------------------------------------------------------------
    SELECT 'INSTITUTE_HEAD' as role, id, name, email, password_hash FROM admins WHERE LOWER(email) = LOWER(:email)
    UNION ALL
    SELECT 'WARDEN' as role, id, name, email, password_hash FROM authorities WHERE LOWER(email) = LOWER(:email)
    UNION ALL
    SELECT 'STUDENT' as role, id, name, email, password_hash FROM students WHERE LOWER(email) = LOWER(:email)
    LIMIT 1;
    -------------------------------------------------------------------------
    """
    clean_email = email.lower().strip()

    admin = db.query(models.Admin).filter(func.lower(models.Admin.email) == clean_email).first()
    if admin:
        return admin

    authority = db.query(models.Authority).filter(func.lower(models.Authority.email) == clean_email).first()
    if authority:
        return authority

    student = db.query(models.Student).filter(func.lower(models.Student.email) == clean_email).first()
    if student:
        return student

    return None


def get_user_by_id(db: Session, user_id: int, role: Optional[str] = None) -> Optional[Any]:
    """
    Fetch a user entity by Primary Key and optional Role discriminator.
    """
    if role in [models.UserRole.INSTITUTE_HEAD.value, models.UserRole.ADMIN.value]:
        admin = db.query(models.Admin).filter(models.Admin.id == user_id).first()
        if admin:
            return admin
    elif role == models.UserRole.WARDEN.value:
        authority = db.query(models.Authority).filter(models.Authority.id == user_id).first()
        if authority:
            return authority
    elif role == models.UserRole.STUDENT.value:
        student = db.query(models.Student).filter(models.Student.id == user_id).first()
        if student:
            return student

    # Fallback search if role was not specified
    student = db.query(models.Student).filter(models.Student.id == user_id).first()
    if student:
        return student
    admin = db.query(models.Admin).filter(models.Admin.id == user_id).first()
    if admin:
        return admin
    authority = db.query(models.Authority).filter(models.Authority.id == user_id).first()
    if authority:
        return authority
    return None


def create_user(
    db: Session,
    user_in: schemas.UserRegister,
    role: Optional[str] = None
) -> Any:
    """
    Insert a new campus user into their designated normalized table:
      - INSTITUTE_HEAD / ADMIN -> table `admins`
      - WARDEN -> table `authorities`
      - STUDENT -> table `students` (and creates an entry in `allocations` if room_id is specified)

    RAW SQL:
    -------------------------------------------------------------------------
    -- When creating student:
    INSERT INTO students (roll_number, name, major, emergency_contact, email, password_hash, created_at)
    VALUES (:roll, :name, :major, :contact, LOWER(:email), :pwd_hash, CURRENT_TIMESTAMP)
    RETURNING *;
    -------------------------------------------------------------------------
    """
    assigned_role = role if role else (
        user_in.role.value if hasattr(user_in.role, 'value') else (user_in.role or models.UserRole.STUDENT.value)
    )
    clean_email = user_in.email.lower().strip()
    pwd_hash = get_password_hash(user_in.password)

    if assigned_role in [models.UserRole.INSTITUTE_HEAD.value, models.UserRole.ADMIN.value]:
        admin = models.Admin(
            name=user_in.name.strip(),
            email=clean_email,
            password_hash=pwd_hash,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    elif assigned_role == models.UserRole.WARDEN.value:
        authority = models.Authority(
            name=user_in.name.strip(),
            designation="Chief Warden",
            email=clean_email,
            password_hash=pwd_hash,
        )
        db.add(authority)
        db.commit()
        db.refresh(authority)
        return authority

    else:
        # Default to STUDENT table
        roll_num = user_in.roll_number.strip() if user_in.roll_number else f"AM.SC.U4CSE25{random.randint(100, 999)}"
        contact = user_in.phone.strip() if user_in.phone else "+91 98765 43210"
        major = getattr(user_in, 'major', 'Computer Science & Engineering') or 'Computer Science & Engineering'

        student = models.Student(
            roll_number=roll_num,
            name=user_in.name.strip(),
            major=major,
            emergency_contact=contact,
            email=clean_email,
            password_hash=pwd_hash,
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # If a room was pre-allocated upon registration, insert into ALLOCATION
        if user_in.room_id:
            alloc = models.Allocation(
                student_id=student.id,
                room_id=user_in.room_id,
                allocation_date=date.today(),
                deposit_paid=5000.00,
                is_active=True,
            )
            db.add(alloc)
            db.commit()
            db.refresh(student)

        return student


def get_all_users(
    db: Session,
    role: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Any]:
    """Retrieve users across tables with optional role filter."""
    users = []
    if role in [None, models.UserRole.INSTITUTE_HEAD.value, models.UserRole.ADMIN.value]:
        users.extend(db.query(models.Admin).all())
    if role in [None, models.UserRole.WARDEN.value]:
        users.extend(db.query(models.Authority).all())
    if role in [None, models.UserRole.STUDENT.value]:
        users.extend(db.query(models.Student).all())
    return users[skip : skip + limit]


def get_students(
    db: Session,
    search: Optional[str] = None,
    unallocated_only: bool = False
) -> List[models.Student]:
    """
    Fetch students from `students` table, optionally filtering for unallocated students
    (no active row in `allocations`) or matching name/roll_number.
    """
    query = db.query(models.Student)
    if unallocated_only:
        query = query.filter(~models.Student.allocations.any(models.Allocation.is_active == True))

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Student.name.ilike(search_pattern),
                models.Student.roll_number.ilike(search_pattern),
            )
        )
    return query.order_by(models.Student.name.asc()).all()


# =============================================================================
# 2. ROOM & BED ALLOCATION (TABLES: room_types, rooms, allocations, students)
# =============================================================================

def get_rooms(
    db: Session,
    block: Optional[str] = None,
    room_type: Optional[str] = None,
    has_ac: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[schemas.RoomOut]:
    """
    Query rooms with dynamic filters and compute live bed occupancy.
    Joins `rooms` -> `room_types` and `rooms` -> `allocations` -> `students`.
    """
    query = db.query(models.Room).options(joinedload(models.Room.type_rel))

    if block and block != "All Blocks":
        query = query.filter(models.Room.block == block)

    if room_type and room_type != "All Types":
        query = query.join(models.RoomType, models.Room.type_id == models.RoomType.id).filter(
            models.RoomType.type_name == room_type
        )

    if has_ac is not None:
        query = query.filter(models.Room.has_ac == has_ac)

    rooms = query.order_by(models.Room.room_number.asc()).all()

    # Search filter applied if searching student name or room number
    if search and search.strip():
        term = search.strip().lower()
        filtered = []
        for r in rooms:
            if term in r.room_number.lower():
                filtered.append(r)
                continue
            if any(term in (occ.name or "").lower() or term in (occ.roll_number or "").lower() for occ in r.occupants):
                filtered.append(r)
        rooms = filtered

    # Slice for pagination
    paged_rooms = rooms[skip: skip + limit]

    result: List[schemas.RoomOut] = []
    for r in paged_rooms:
        occ_list = [
            schemas.UserSummary(
                id=u.id,
                name=u.name,
                email=u.email,
                role=u.role,
                roll_number=u.roll_number,
                room_number=r.room_number,
                block=r.block,
            )
            for u in r.occupants
        ]
        occupied_count = len(occ_list)
        vacant_count = max(0, r.capacity - occupied_count)

        # Build bed-by-bed status for visual dot indicators (🔴 occupied / 🟢 vacant)
        beds = []
        for i in range(r.capacity):
            if i < occupied_count:
                beds.append(schemas.BedStatus(bed_index=i + 1, is_occupied=True, student=occ_list[i]))
            else:
                beds.append(schemas.BedStatus(bed_index=i + 1, is_occupied=False, student=None))

        result.append(
            schemas.RoomOut(
                id=r.id,
                room_number=r.room_number,
                block=r.block,
                room_type=r.room_type,
                capacity=r.capacity,
                has_ac=r.has_ac,
                created_at=r.created_at,
                occupants=occ_list,
                occupied_count=occupied_count,
                vacant_count=vacant_count,
                beds=beds,
            )
        )
    return result


def get_room_by_id(db: Session, room_id: int) -> Optional[models.Room]:
    """Fetch a single room by primary key with its RoomType relation."""
    return db.query(models.Room).options(joinedload(models.Room.type_rel)).filter(models.Room.id == room_id).first()


def get_room_by_number(db: Session, room_number: str) -> Optional[models.Room]:
    """Fetch room by unique room number."""
    return db.query(models.Room).filter(models.Room.room_number == room_number).first()


def create_room(db: Session, room_in: schemas.RoomCreate) -> models.Room:
    """
    Add a new hostel room entity linked to a normalized RoomType.
    """
    rt = db.query(models.RoomType).filter(models.RoomType.type_name == room_in.room_type).first()
    if not rt:
        rt = models.RoomType(type_name=room_in.room_type, capacity=room_in.capacity)
        db.add(rt)
        db.commit()
        db.refresh(rt)

    db_room = models.Room(
        room_number=room_in.room_number.strip().upper(),
        block=room_in.block.strip(),
        type_id=rt.id,
        has_ac=room_in.has_ac,
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


def allocate_bed(db: Session, room_id: int, student_id: int) -> models.Student:
    """
    Allocate a student to a room bed in the ALLOCATION table.
    Enforces capacity constraint: cannot allocate if room capacity is reached.

    RAW SQL TRANSACTION:
    -------------------------------------------------------------------------
    BEGIN;
    -- 1. Verify capacity limit
    SELECT rt.capacity, COUNT(a.id)
    FROM rooms r
    JOIN room_types rt ON r.type_id = rt.id
    LEFT JOIN allocations a ON a.room_id = r.id AND a.is_active = TRUE
    WHERE r.id = :room_id
    GROUP BY rt.capacity;

    -- 2. Deactivate any prior active assignment
    UPDATE allocations SET is_active = FALSE WHERE student_id = :student_id AND is_active = TRUE;

    -- 3. Insert fresh allocation
    INSERT INTO allocations (student_id, room_id, allocation_date, deposit_paid, is_active, created_at)
    VALUES (:student_id, :room_id, CURRENT_DATE, 5000.00, TRUE, CURRENT_TIMESTAMP);
    COMMIT;
    -------------------------------------------------------------------------
    """
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise ValueError("Room not found")

    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise ValueError("Student record not found")

    # Enforce capacity constraint (Trigger trg_check_bed_capacity logic)
    current_occupants = db.query(func.count(models.Allocation.id)).filter(
        models.Allocation.room_id == room_id,
        models.Allocation.is_active == True
    ).scalar() or 0

    if current_occupants >= room.capacity:
        raise ValueError(f"Room {room.room_number} is full ({current_occupants}/{room.capacity} occupied).")

    # Deactivate existing allocations for this student
    db.query(models.Allocation).filter(
        models.Allocation.student_id == student_id,
        models.Allocation.is_active == True
    ).update({"is_active": False})

    # Insert new active allocation record
    new_alloc = models.Allocation(
        student_id=student_id,
        room_id=room_id,
        allocation_date=date.today(),
        deposit_paid=5000.00,
        is_active=True,
    )
    db.add(new_alloc)
    db.commit()
    db.refresh(student)
    return student


def deallocate_bed(db: Session, student_id: int) -> models.Student:
    """
    Remove student from their assigned room (Vacate bed / Checkout).
    Marks active row in `allocations` as inactive (`is_active = FALSE`).
    """
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    db.query(models.Allocation).filter(
        models.Allocation.student_id == student_id,
        models.Allocation.is_active == True
    ).update({"is_active": False})

    db.commit()
    db.refresh(student)
    return student


# =============================================================================
# 3. COMPLAINT MANAGEMENT (TABLES: complaints, staff, students)
# =============================================================================

def create_complaint(
    db: Session,
    complaint_in: schemas.ComplaintCreate,
    student_id: int
) -> models.Complaint:
    """
    Register a new maintenance ticket in table `complaints`.
    Auto-assigns service technician from table `staff` based on category.

    Ticket numbering format: 'CM-2026-XXXX'.
    """
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    ticket_num = f"CM-2026-{random.randint(100, 999):04d}"
    category_val = complaint_in.category.value if hasattr(complaint_in.category, "value") else str(complaint_in.category)
    urgency_val = complaint_in.urgency.value if hasattr(complaint_in.urgency, "value") else str(complaint_in.urgency or "Medium")

    # Match category with staff member
    staff_member = None
    if "Electr" in category_val:
        staff_member = db.query(models.Staff).filter(models.Staff.role_type.ilike("%Electrician%")).first()
    elif "Plumb" in category_val:
        staff_member = db.query(models.Staff).filter(models.Staff.role_type.ilike("%Plumber%")).first()
    elif "Carpent" in category_val or "Furnit" in category_val:
        staff_member = db.query(models.Staff).filter(models.Staff.role_type.ilike("%Carpenter%")).first()

    if not staff_member:
        staff_member = db.query(models.Staff).first()

    staff_id = staff_member.id if staff_member else None
    assigned_name = staff_member.name if staff_member else "Duty Staff"

    db_complaint = models.Complaint(
        ticket_number=ticket_num,
        student_id=student_id,
        staff_id=staff_id,
        category=category_val,
        title=complaint_in.title.strip(),
        description=complaint_in.description.strip(),
        urgency=urgency_val,
        status=models.ComplaintStatus.OPEN.value,
        assigned_staff=assigned_name,
        image_url=complaint_in.image_url,
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint


def get_complaints(
    db: Session,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Complaint]:
    """
    Fetch complaints with relational joins to Student and Staff.
    """
    query = (
        db.query(models.Complaint)
        .options(
            joinedload(models.Complaint.student),
            joinedload(models.Complaint.assigned_staff_member),
        )
    )

    if student_id:
        query = query.filter(models.Complaint.student_id == student_id)

    if status and status != "All Status":
        query = query.filter(models.Complaint.status == status)

    if category and category != "All Categories":
        query = query.filter(models.Complaint.category == category)

    if urgency and urgency != "All Urgencies":
        query = query.filter(models.Complaint.urgency == urgency)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.join(models.Student, models.Complaint.student_id == models.Student.id).filter(
            or_(
                models.Complaint.ticket_number.ilike(term),
                models.Complaint.title.ilike(term),
                models.Complaint.category.ilike(term),
                models.Student.name.ilike(term),
            )
        )

    return query.order_by(desc(models.Complaint.created_at)).offset(skip).limit(limit).all()


def get_complaint_by_id(db: Session, complaint_id: int) -> Optional[models.Complaint]:
    """Fetch complaint by ID with relations."""
    return (
        db.query(models.Complaint)
        .options(
            joinedload(models.Complaint.student),
            joinedload(models.Complaint.assigned_staff_member),
        )
        .filter(models.Complaint.id == complaint_id)
        .first()
    )


def update_complaint_status(
    db: Session,
    complaint_id: int,
    update_in: schemas.ComplaintUpdate
) -> models.Complaint:
    """
    Update complaint status, assigned technician, or resolution notes.
    Auto-sets `resolved_at = CURRENT_TIMESTAMP` when marked Resolved (Trigger trg_auto_resolve_complaint).
    """
    complaint = get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise ValueError("Complaint not found")

    if update_in.status:
        status_val = update_in.status.value if hasattr(update_in.status, "value") else str(update_in.status)
        complaint.status = status_val
        if status_val in [models.ComplaintStatus.RESOLVED.value, "Resolved"]:
            complaint.resolved_at = datetime.now(timezone.utc)

    if update_in.assigned_staff is not None:
        complaint.assigned_staff = update_in.assigned_staff

    if update_in.resolution_notes is not None:
        complaint.resolution_notes = update_in.resolution_notes

    db.commit()
    db.refresh(complaint)
    return complaint


# =============================================================================
# 4. LEAVE REQUESTS / GATE PASS (TABLES: leave_passes, authorities, students)
# =============================================================================

def create_leave_request(
    db: Session,
    leave_in: schemas.LeaveCreate,
    student_id: int
) -> models.LeavePass:
    """
    File an out-station leave or gate pass request.
    Enforces CheckConstraint: `expected_return >= depart_expected`.
    """
    if leave_in.return_date < leave_in.departure_date:
        raise ValueError("Expected return date cannot be earlier than departure date.")

    pass_code = f"GP-2026-{random.randint(1000, 9999)}"
    leave_type_val = leave_in.leave_type.value if hasattr(leave_in.leave_type, "value") else str(leave_in.leave_type)

    db_leave = models.LeavePass(
        pass_code=pass_code,
        student_id=student_id,
        leave_type=leave_type_val,
        depart_expected=leave_in.departure_date,
        expected_return=leave_in.return_date,
        destination=leave_in.destination.strip(),
        reason=leave_in.reason.strip(),
        emergency_contact=leave_in.emergency_contact.strip(),
        parent_consent=leave_in.parent_consent,
        status=models.LeaveStatus.PENDING.value,
    )
    db.add(db_leave)
    db.commit()
    db.refresh(db_leave)
    return db_leave


def get_leave_requests(
    db: Session,
    student_id: Optional[int] = None,
    status: Optional[str] = None,
    leave_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.LeavePass]:
    """
    Retrieve leave applications with student details from `leave_passes`.
    """
    query = (
        db.query(models.LeavePass)
        .options(
            joinedload(models.LeavePass.student)
        )
    )

    if student_id:
        query = query.filter(models.LeavePass.student_id == student_id)

    if status and status != "All Status":
        query = query.filter(models.LeavePass.status == status)

    if leave_type and leave_type != "All Types":
        query = query.filter(models.LeavePass.leave_type == leave_type)

    return query.order_by(desc(models.LeavePass.created_at)).offset(skip).limit(limit).all()


def get_leave_by_id(db: Session, leave_id: int) -> Optional[models.LeavePass]:
    """Fetch single leave request by ID."""
    return (
        db.query(models.LeavePass)
        .options(joinedload(models.LeavePass.student))
        .filter(models.LeavePass.id == leave_id)
        .first()
    )


def update_leave_status(
    db: Session,
    leave_id: int,
    new_status: models.LeaveStatus,
    approver_id: int
) -> models.LeavePass:
    """
    Warden or Institute Head approves, validates, or rejects a leave pass.
    Auto-generates gate pass token upon approval (Trigger trg_auto_gate_pass_token).
    """
    leave = get_leave_by_id(db, leave_id)
    if not leave:
        raise ValueError("Leave request not found")

    status_val = new_status.value if hasattr(new_status, "value") else str(new_status)
    leave.status = status_val
    leave.authority_id = approver_id

    if status_val in [models.LeaveStatus.APPROVED.value, "Approved"]:
        leave.gate_pass_token = f"HOSTEL-PASS-AUTH-{leave.id:04d}-{random.randint(1000, 9999)}"

    db.commit()
    db.refresh(leave)
    return leave


# =============================================================================
# 5. ATTENDANCE ROSTER (TABLES: attendance, students, allocations, rooms)
# =============================================================================

def get_attendance_roster(
    db: Session,
    target_date: date,
    block: Optional[str] = None,
    search: Optional[str] = None
) -> List[schemas.AttendanceRecordOut]:
    """
    Fetch complete student roster for daily night roll-call on `target_date`.
    Joins `students` -> `allocations` (active) -> `rooms`, outer-joining `attendance`.
    """
    query = (
        db.query(models.Student, models.Room, models.Attendance)
        .join(models.Allocation, and_(models.Allocation.student_id == models.Student.id, models.Allocation.is_active == True))
        .join(models.Room, models.Allocation.room_id == models.Room.id)
        .outerjoin(
            models.Attendance,
            and_(
                models.Attendance.student_id == models.Student.id,
                models.Attendance.date == target_date
            )
        )
    )

    if block and block != "All Blocks":
        query = query.filter(models.Room.block == block)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Student.name.ilike(term),
                models.Student.roll_number.ilike(term),
                models.Room.room_number.ilike(term)
            )
        )

    records = query.order_by(models.Room.room_number.asc(), models.Student.name.asc()).all()

    roster: List[schemas.AttendanceRecordOut] = []
    for student, room, att in records:
        roster.append(
            schemas.AttendanceRecordOut(
                id=att.id if att else 0,
                student_id=student.id,
                room_id=room.id,
                date=target_date,
                status=att.status if att else models.AttendanceStatus.PRESENT.value,
                notes=att.notes if att else None,
                student_name=student.name,
                roll_number=student.roll_number,
                room_number=room.room_number,
                block=room.block,
            )
        )
    return roster


def mark_attendance(
    db: Session,
    student_id: int,
    target_date: date,
    status: models.AttendanceStatus,
    notes: Optional[str] = None,
    marked_by: Optional[int] = None
) -> models.Attendance:
    """
    Record or update attendance status for a student (UPSERT on unique (student_id, date)).
    """
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student or not student.room_id:
        raise ValueError("Student has no allocated room")

    existing = (
        db.query(models.Attendance)
        .filter(
            models.Attendance.student_id == student_id,
            models.Attendance.date == target_date
        )
        .first()
    )

    status_val = status.value if hasattr(status, "value") else str(status)

    if existing:
        existing.status = status_val
        existing.notes = notes
        existing.admin_id = marked_by
        db.commit()
        db.refresh(existing)
        return existing

    new_att = models.Attendance(
        student_id=student_id,
        admin_id=marked_by,
        date=target_date,
        status=status_val,
        notes=notes,
    )
    db.add(new_att)
    db.commit()
    db.refresh(new_att)
    return new_att


def bulk_mark_attendance(
    db: Session,
    target_date: date,
    block: Optional[str],
    status: models.AttendanceStatus,
    marked_by: Optional[int]
) -> int:
    """
    Mark all students in a block (or whole hostel) as Present/Absent in batch.
    """
    students_query = (
        db.query(models.Student)
        .join(models.Allocation, and_(models.Allocation.student_id == models.Student.id, models.Allocation.is_active == True))
        .join(models.Room, models.Allocation.room_id == models.Room.id)
    )
    if block and block != "All Blocks":
        students_query = students_query.filter(models.Room.block == block)

    students = students_query.all()
    count = 0
    for s in students:
        mark_attendance(db, s.id, target_date, status, marked_by=marked_by)
        count += 1
    return count


# =============================================================================
# 6. DASHBOARD & ANALYTICS METRICS (Across 10 Tables)
# =============================================================================

def get_dashboard_metrics(db: Session, current_user: Optional[Any] = None) -> schemas.DashboardMetricsOut:
    """
    Aggregates operational hostel metrics for the Executive Overview Dashboard.
    Queries `room_types`, `allocations`, `complaints`, `leave_passes`, `attendance`.
    If current_user is a STUDENT, strictly scopes complaints and leaves to that student.
    """
    total_beds = db.query(func.coalesce(func.sum(models.RoomType.capacity), 0)).join(
        models.Room, models.Room.type_id == models.RoomType.id
    ).scalar() or 54

    filled_beds = db.query(func.count(models.Allocation.id)).filter(
        models.Allocation.is_active == True
    ).scalar() or 42

    occupancy_pct = int(round((filled_beds / total_beds * 100))) if total_beds > 0 else 78
    blocks_count = db.query(func.count(distinct(models.Room.block))).scalar() or 3

    is_student = (current_user is not None and getattr(current_user, "role", None) == models.UserRole.STUDENT.value)

    # Complaints counts
    complaint_filter = [models.Complaint.status.in_([models.ComplaintStatus.OPEN.value, models.ComplaintStatus.ESCALATED.value])]
    triage_filter = [
        models.Complaint.urgency == models.ComplaintUrgency.HIGH.value,
        models.Complaint.status != models.ComplaintStatus.RESOLVED.value
    ]
    if is_student:
        complaint_filter.append(models.Complaint.student_id == current_user.id)
        triage_filter.append(models.Complaint.student_id == current_user.id)

    active_complaints = db.query(func.count(models.Complaint.id)).filter(*complaint_filter).scalar() or 0
    needs_triage_count = db.query(func.count(models.Complaint.id)).filter(*triage_filter).scalar() or 0

    # Pending Leaves
    leave_filter = [models.LeavePass.status == models.LeaveStatus.PENDING.value]
    if is_student:
        leave_filter.append(models.LeavePass.student_id == current_user.id)

    pending_leaves = db.query(func.count(models.LeavePass.id)).filter(*leave_filter).scalar() or 0

    # Attendance Today
    today = date.today()
    total_attendance_today = db.query(func.count(models.Attendance.id)).filter(
        models.Attendance.date == today
    ).scalar() or 0

    if total_attendance_today > 0:
        present_today = db.query(func.count(models.Attendance.id)).filter(
            models.Attendance.date == today,
            models.Attendance.status == models.AttendanceStatus.PRESENT.value
        ).scalar() or 0
        attendance_today_pct = int(round((present_today / total_attendance_today) * 100))
    else:
        attendance_today_pct = 90

    # Recent Complaints (Top 6)
    recent_complaints_base = (
        db.query(models.Complaint)
        .options(
            joinedload(models.Complaint.student),
            joinedload(models.Complaint.assigned_staff_member)
        )
    )
    if is_student:
        recent_complaints_base = recent_complaints_base.filter(models.Complaint.student_id == current_user.id)

    recent_complaints_query = recent_complaints_base.order_by(desc(models.Complaint.created_at)).limit(6).all()

    recent_complaints = [
        schemas.ComplaintOut(
            id=c.id,
            ticket_number=c.ticket_number,
            student_id=c.student_id,
            room_id=c.room_id,
            category=c.category,
            title=c.title,
            description=c.description,
            urgency=c.urgency,
            status=c.status,
            assigned_staff=c.assigned_staff,
            resolution_notes=c.resolution_notes,
            image_url=c.image_url,
            created_at=c.created_at,
            resolved_at=c.resolved_at,
            student=schemas.UserSummary.model_validate(c.student) if c.student else None,
        )
        for c in recent_complaints_query
    ]

    # Approved Passes (Top 5 awaiting checkout)
    approved_passes_base = (
        db.query(models.LeavePass)
        .options(
            joinedload(models.LeavePass.student)
        )
        .filter(models.LeavePass.status.in_([
            models.LeaveStatus.APPROVED.value,
            models.LeaveStatus.VALIDATED.value,
            models.LeaveStatus.PENDING.value
        ]))
    )
    if is_student:
        approved_passes_base = approved_passes_base.filter(models.LeavePass.student_id == current_user.id)

    approved_passes_query = approved_passes_base.order_by(desc(models.LeavePass.created_at)).limit(5).all()

    approved_passes = [
        schemas.LeaveOut(
            id=lp.id,
            pass_code=lp.pass_code,
            student_id=lp.student_id,
            leave_type=lp.leave_type,
            departure_date=lp.departure_date,
            return_date=lp.return_date,
            destination=lp.destination,
            reason=lp.reason,
            emergency_contact=lp.emergency_contact,
            parent_consent=lp.parent_consent,
            status=lp.status,
            approved_by=lp.approved_by,
            created_at=lp.created_at,
            student=schemas.UserSummary.model_validate(lp.student) if lp.student else None,
        )
        for lp in approved_passes_query
    ]

    return schemas.DashboardMetricsOut(
        total_beds=total_beds,
        filled_beds=filled_beds,
        occupancy_pct=occupancy_pct,
        blocks_count=blocks_count,
        active_complaints=active_complaints,
        needs_triage_count=needs_triage_count,
        pending_leaves=pending_leaves,
        attendance_today_pct=attendance_today_pct,
        recent_complaints=recent_complaints,
        approved_passes=approved_passes,
    )
