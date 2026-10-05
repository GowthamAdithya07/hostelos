"""
=============================================================================
HOSTELOS - DATA VALIDATION & SERIALIZATION SCHEMAS (Pydantic DTOs)
=============================================================================
Enforces data integrity, validation rules, and schema contracts.
=============================================================================
"""

from datetime import datetime, date
from typing import Optional, List, Union
from pydantic import BaseModel, EmailStr, Field
from .models import (
    UserRole,
    ComplaintCategory,
    ComplaintUrgency,
    ComplaintStatus,
    LeaveType,
    LeaveStatus,
    AttendanceStatus,
)


# =============================================================================
# 1. USER SCHEMAS
# =============================================================================

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserRegister(UserBase):
    password: str = Field(..., min_length=4, max_length=100)
    role: Optional[Union[UserRole, str]] = UserRole.STUDENT
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    room_id: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class QuickSwitchRequest(BaseModel):
    email: EmailStr


class UserSummary(BaseModel):
    id: int
    name: str
    email: str
    role: str
    roll_number: Optional[str] = None
    room_number: Optional[str] = None
    block: Optional[str] = None

    class Config:
        from_attributes = True


class UserOut(UserBase):
    id: int
    role: str
    roll_number: Optional[str] = None
    phone: Optional[str] = None
    room_id: Optional[int] = None
    room_number: Optional[str] = None
    block: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# 2. AUTH & TOKEN SCHEMAS
# =============================================================================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


# =============================================================================
# 3. ROOM SCHEMAS
# =============================================================================

class RoomBase(BaseModel):
    room_number: str
    block: str
    room_type: str
    capacity: int = 2
    has_ac: bool = False


class RoomCreate(RoomBase):
    pass


class BedStatus(BaseModel):
    bed_index: int
    is_occupied: bool
    student: Optional[UserSummary] = None


class RoomOut(RoomBase):
    id: int
    created_at: datetime
    occupants: List[UserSummary] = []
    occupied_count: int = 0
    vacant_count: int = 0
    beds: List[BedStatus] = []

    class Config:
        from_attributes = True


class AllocateBedRequest(BaseModel):
    student_id: int
    room_id: int


# =============================================================================
# 4. COMPLAINT SCHEMAS
# =============================================================================

class ComplaintCreate(BaseModel):
    category: Union[ComplaintCategory, str]
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    urgency: Optional[Union[ComplaintUrgency, str]] = ComplaintUrgency.MEDIUM
    image_url: Optional[str] = None


class ComplaintUpdate(BaseModel):
    status: Optional[Union[ComplaintStatus, str]] = None
    assigned_staff: Optional[str] = None
    resolution_notes: Optional[str] = None


class ComplaintOut(BaseModel):
    id: int
    ticket_number: str
    student_id: int
    room_id: Optional[int] = None
    category: str
    title: str
    description: str
    urgency: str
    status: str
    assigned_staff: Optional[str] = None
    resolution_notes: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    student: Optional[UserSummary] = None

    class Config:
        from_attributes = True


# =============================================================================
# 5. LEAVE REQUEST SCHEMAS
# =============================================================================

class LeaveCreate(BaseModel):
    leave_type: Union[LeaveType, str]
    departure_date: datetime
    return_date: datetime
    destination: str = Field(..., min_length=1, max_length=255)
    reason: str = Field(..., min_length=1, max_length=1000)
    emergency_contact: str = Field(..., min_length=3, max_length=50)
    parent_consent: bool = True


class LeaveStatusUpdate(BaseModel):
    status: Union[LeaveStatus, str]


class LeaveOut(BaseModel):
    id: int
    pass_code: str
    student_id: int
    leave_type: str
    departure_date: datetime
    return_date: datetime
    destination: str
    reason: str
    emergency_contact: str
    parent_consent: bool
    status: str
    approved_by: Optional[int] = None
    created_at: datetime
    student: Optional[UserSummary] = None

    class Config:
        from_attributes = True


# =============================================================================
# 6. ATTENDANCE SCHEMAS
# =============================================================================

class AttendanceMark(BaseModel):
    student_id: int
    date: date
    status: Union[AttendanceStatus, str] = AttendanceStatus.PRESENT
    notes: Optional[str] = None


class AttendanceBulkMark(BaseModel):
    date: date
    block: Optional[str] = None
    status: Union[AttendanceStatus, str] = AttendanceStatus.PRESENT


class AttendanceRecordOut(BaseModel):
    id: int
    student_id: int
    room_id: int
    date: date
    status: str
    notes: Optional[str] = None
    student_name: str
    roll_number: Optional[str] = None
    room_number: str
    block: str

    class Config:
        from_attributes = True


# =============================================================================
# 7. DASHBOARD METRICS SCHEMAS
# =============================================================================

class DashboardMetricsOut(BaseModel):
    total_beds: int
    filled_beds: int
    occupancy_pct: int
    blocks_count: int
    active_complaints: int
    needs_triage_count: int
    pending_leaves: int
    attendance_today_pct: int
    recent_complaints: List[ComplaintOut] = []
    approved_passes: List[LeaveOut] = []
