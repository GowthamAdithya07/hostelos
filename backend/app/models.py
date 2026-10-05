"""
=============================================================================
HOSTELOS - 10-TABLE RELATIONAL DATABASE ORM MODELS (SQLAlchemy)
=============================================================================
Course: 23CSE202 - Database Management Systems (Group C9)
Reference Document: Copy of 03. DB Design.docx (Section 3.3 Relational Schema)

10 RELATIONAL TABLES IN BOYCE-CODD NORMAL FORM (BCNF / 3NF):
  1. STUDENT    (student_id [PK], name, major, emergency_contact, email, password_hash)
  2. ROOM_TYPE  (type_id [PK], type_name, capacity)
  3. ROOM       (room_id [PK], block, room_number, type_id [FK])
  4. ALLOCATION (allocation_id [PK], student_id [FK], room_id [FK], allocation_date, deposit_paid, is_active)
  5. ADMIN      (admin_id [PK], name, email, password_hash)
  6. STAFF      (staff_id [PK], name, role_type, phone)
  7. AUTHORITY  (authority_id [PK], name, designation, email, password_hash)
  8. COMPLAINT  (complaint_id [PK], ticket_number, student_id [FK], staff_id [FK], category, title, description, status, urgency, resolution_notes, image_url, created_at, resolved_at)
  9. ATTENDANCE (attendance_id [PK], student_id [FK], admin_id [FK], date, status, notes)
 10. LEAVE_PASS (pass_id [PK], pass_code, student_id [FK], authority_id [FK], leave_type, depart_expected, expected_return, actual_return, destination, reason, emergency_contact, status, rejection_reason, gate_pass_token, created_at)
=============================================================================
"""

import enum
from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship
from .database import Base


# =============================================================================
# ENUMS (DOMAIN INTEGRITY)
# =============================================================================

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    WARDEN = "WARDEN"
    ADMIN = "ADMIN"
    INSTITUTE_HEAD = "INSTITUTE_HEAD"


class ComplaintCategory(str, enum.Enum):
    PLUMBING = "Plumbing"
    ELECTRICAL = "Electrical & Lighting"
    INTERNET = "Internet Connectivity"
    FURNITURE = "Carpentry / Furniture"
    HOUSEKEEPING = "Housekeeping"
    OTHER = "Other"


class ComplaintUrgency(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ComplaintStatus(str, enum.Enum):
    OPEN = "Open"
    ESCALATED = "Escalated"
    RESOLVED = "Resolved"


class LeaveType(str, enum.Enum):
    WEEKEND = "Weekend outing"
    EMERGENCY = "Emergency leave"
    VACATION = "Vacation"


class LeaveStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    VALIDATED = "Validated"
    REJECTED = "Rejected"
    CHECKED_OUT = "Checked Out"
    RETURNED = "Returned"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late / Permitted"


# =============================================================================
# 1. ENTITY: STUDENT (Table 1 of 10)
# =============================================================================

class Student(Base):
    """
    STUDENT (StudentID [PK], Name, Major, EmergencyContact, Email, PasswordHash)
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)  # e.g., 'AM.SC.U4CSE25209'
    name = Column(String(255), nullable=False)
    major = Column(String(255), nullable=False, default="Computer Science & Engineering")
    emergency_contact = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    allocations = relationship("Allocation", back_populates="student", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    leave_passes = relationship("LeavePass", back_populates="student", cascade="all, delete-orphan")

    @property
    def role(self):
        return UserRole.STUDENT.value

    @property
    def active_allocation(self):
        return next((a for a in self.allocations if a.is_active), None)

    @property
    def room(self):
        alloc = self.active_allocation
        return alloc.room if alloc else None

    @property
    def room_number(self):
        alloc = self.active_allocation
        return alloc.room.room_number if (alloc and alloc.room) else None

    @property
    def block(self):
        alloc = self.active_allocation
        return alloc.room.block if (alloc and alloc.room) else None

    @property
    def room_id(self):
        alloc = self.active_allocation
        return alloc.room_id if alloc else None


# =============================================================================
# 2. ENTITY: ROOM_TYPE (Table 2 of 10)
# =============================================================================

class RoomType(Base):
    """
    ROOM_TYPE (TypeID [PK], TypeName, Capacity)
    Extracts type details out of ROOM to prevent 3NF transitive dependency.
    """
    __tablename__ = "room_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type_name = Column(String(100), unique=True, nullable=False)  # e.g., 'Single AC', 'Double AC', 'Double Non-AC'
    capacity = Column(Integer, nullable=False, default=2)

    # Relationship
    rooms = relationship("Room", back_populates="type_rel")


# =============================================================================
# 3. ENTITY: ROOM (Table 3 of 10)
# =============================================================================

class Room(Base):
    """
    ROOM (RoomID [PK], Block, RoomNumber, TypeID [FK])
    """
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint("block", "room_number", name="uq_block_room_number"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    block = Column(String(50), nullable=False, index=True)         # 'Block A', 'Block B', 'Block C'
    room_number = Column(String(50), nullable=False, index=True)   # 'A-101', 'B-202'
    type_id = Column(Integer, ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False)
    has_ac = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    type_rel = relationship("RoomType", back_populates="rooms")
    allocations = relationship("Allocation", back_populates="room", cascade="all, delete-orphan")

    @property
    def capacity(self):
        return self.type_rel.capacity if self.type_rel else 2

    @property
    def room_type(self):
        return self.type_rel.type_name if self.type_rel else "Standard"

    @property
    def active_allocations(self):
        return [a for a in self.allocations if a.is_active]

    @property
    def occupants(self):
        return [a.student for a in self.active_allocations if a.student]


# =============================================================================
# 4. ENTITY: ALLOCATION (Table 4 of 10)
# =============================================================================

class Allocation(Base):
    """
    ALLOCATION (AllocationID [PK], StudentID [FK], RoomID [FK], AllocationDate, DepositPaid)
    Enables tracking a student's room-assignment history over time.
    """
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    allocation_date = Column(Date, nullable=False, default=date.today)
    deposit_paid = Column(Numeric(10, 2), nullable=False, default=5000.00)
    is_active = Column(Boolean, nullable=False, default=True)  # True = current occupant, False = vacated/checked out
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="allocations")
    room = relationship("Room", back_populates="allocations")


# =============================================================================
# 5. ENTITY: ADMIN (Table 5 of 10)
# =============================================================================

class Admin(Base):
    """
    ADMIN (AdminID [PK], Name, Email, PasswordHash)
    Executive College Administrator / Institute Head.
    """
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    attendance_records = relationship("Attendance", back_populates="admin")

    @property
    def role(self):
        return UserRole.INSTITUTE_HEAD.value

    @property
    def roll_number(self):
        return None

    @property
    def phone(self):
        return None

    @property
    def room_id(self):
        return None

    @property
    def room_number(self):
        return None

    @property
    def block(self):
        return None

    @property
    def major(self):
        return None

    @property
    def emergency_contact(self):
        return None


# =============================================================================
# 6. ENTITY: STAFF (Table 6 of 10)
# =============================================================================

class Staff(Base):
    """
    STAFF (StaffID [PK], Name, RoleType, Phone)
    Maintenance technicians & service staff (Electricians, Plumbers, Carpenters).
    """
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    role_type = Column(String(100), nullable=False)  # 'Senior Electrician', 'Plumber', 'Carpenter', 'Housekeeping'
    phone = Column(String(50), nullable=False)

    # Relationships
    complaints = relationship("Complaint", back_populates="assigned_staff_member")


# =============================================================================
# 7. ENTITY: AUTHORITY (Table 7 of 10)
# =============================================================================

class Authority(Base):
    """
    AUTHORITY (AuthorityID [PK], Name, Designation, Email, PasswordHash)
    Hostel Wardens and Approving Authorities.
    """
    __tablename__ = "authorities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    designation = Column(String(100), nullable=False, default="Chief Warden")  # 'Chief Warden', 'Deputy Warden', 'Dean'
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    reviewed_leave_passes = relationship("LeavePass", back_populates="authority")

    @property
    def role(self):
        return UserRole.WARDEN.value

    @property
    def roll_number(self):
        return None

    @property
    def phone(self):
        return None

    @property
    def room_id(self):
        return None

    @property
    def room_number(self):
        return None

    @property
    def block(self):
        return None

    @property
    def major(self):
        return None

    @property
    def emergency_contact(self):
        return None


# =============================================================================
# 8. ENTITY: COMPLAINT (Table 8 of 10)
# =============================================================================

class Complaint(Base):
    """
    COMPLAINT (ComplaintID [PK], StudentID [FK], StaffID [FK], Category, Title, Status, Urgency)
    """
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)

    category = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    urgency = Column(String(20), default=ComplaintUrgency.MEDIUM.value, nullable=False)
    status = Column(String(50), default=ComplaintStatus.OPEN.value, nullable=False, index=True)

    assigned_staff = Column(String(255), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student = relationship("Student", back_populates="complaints")
    assigned_staff_member = relationship("Staff", back_populates="complaints")

    @property
    def room_id(self):
        return self.student.room_id if self.student else None

    @property
    def room(self):
        return self.student.room if self.student else None


# =============================================================================
# 9. ENTITY: ATTENDANCE (Table 9 of 10)
# =============================================================================

class Attendance(Base):
    """
    ATTENDANCE (AttendanceID [PK], StudentID [FK], AdminID [FK], Date, Status)
    """
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_student_date_attendance"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    status = Column(String(50), default=AttendanceStatus.PRESENT.value, nullable=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    admin = relationship("Admin", back_populates="attendance_records")

    @property
    def room_id(self):
        return self.student.room_id if self.student else None

    @property
    def marked_by(self):
        return self.admin_id

    @marked_by.setter
    def marked_by(self, val):
        self.admin_id = val

    @property
    def student_name(self):
        return self.student.name if self.student else "Student"

    @property
    def roll_number(self):
        return self.student.roll_number if self.student else None

    @property
    def room_number(self):
        return self.student.room_number if self.student else "Unassigned"

    @property
    def block(self):
        return self.student.block if self.student else "Block A"


# =============================================================================
# 10. ENTITY: LEAVE_PASS (Table 10 of 10)
# =============================================================================

class LeavePass(Base):
    """
    LEAVE_PASS (PassID [PK], StudentID [FK], AuthorityID [FK], LeaveType, DepartExpected, ExpectedReturn, ActualReturn, Status, RejectionReason, GatePassToken)
    """
    __tablename__ = "leave_passes"
    __table_args__ = (
        CheckConstraint("expected_return >= depart_expected", name="chk_leave_dates"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pass_code = Column(String(50), unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    authority_id = Column(Integer, ForeignKey("authorities.id", ondelete="SET NULL"), nullable=True)

    leave_type = Column(String(50), nullable=False)
    depart_expected = Column(DateTime, nullable=False)
    expected_return = Column(DateTime, nullable=False)
    actual_return = Column(DateTime, nullable=True)

    destination = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    emergency_contact = Column(String(50), nullable=False)
    parent_consent = Column(Boolean, default=True, nullable=False)

    status = Column(String(50), default=LeaveStatus.PENDING.value, nullable=False, index=True)
    rejection_reason = Column(Text, nullable=True)
    gate_pass_token = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="leave_passes")
    authority = relationship("Authority", back_populates="reviewed_leave_passes")

    # Compatibility aliases
    @property
    def departure_date(self):
        return self.depart_expected

    @departure_date.setter
    def departure_date(self, val):
        self.depart_expected = val

    @property
    def return_date(self):
        return self.expected_return

    @return_date.setter
    def return_date(self, val):
        self.expected_return = val

    @property
    def approved_by(self):
        return self.authority_id

    @approved_by.setter
    def approved_by(self, val):
        self.authority_id = val


# Compatibility alias for earlier code
LeaveRequest = LeavePass
User = Student
