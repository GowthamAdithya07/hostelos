"""
=============================================================================
HOSTELOS - DAILY ATTENDANCE REGISTER ROUTER (routers/attendance.py)
=============================================================================
API endpoints for:
  - Daily roll-call attendance roster (Present / Absent / Late / Permitted)
  - Filtering by Block and Student Search
  - CSV Export of daily attendance
=============================================================================
"""

import csv
import io
from datetime import date
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, models, crud
from ..auth import get_current_user, get_optional_current_user, get_current_warden_or_admin

router = APIRouter(prefix="/attendance", tags=["Daily Attendance"])


@router.get("", response_model=List[schemas.AttendanceRecordOut])
def get_daily_roster(
    date_str: Optional[str] = Query(None, alias="date", description="YYYY-MM-DD date"),
    block: Optional[str] = Query(None, description="Block A, Block B, Block C"),
    search: Optional[str] = Query(None, description="Student name or roll number"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Fetch daily roll-call roster.
    Matches C9 Hostelos_image4.jpeg.
    """
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    return crud.get_attendance_roster(db, target_date=target_date, block=block, search=search)


@router.post("/mark", response_model=schemas.AttendanceRecordOut)
def mark_single_attendance(
    record_in: schemas.AttendanceMark,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Mark or toggle attendance for an individual student.
    Uses UPSERT on (student_id, date).
    """
    try:
        saved = crud.mark_attendance(
            db,
            student_id=record_in.student_id,
            target_date=record_in.date,
            status=record_in.status,
            notes=record_in.notes,
            marked_by=current_user.id,
        )
        # Fetch updated record DTO
        roster = crud.get_attendance_roster(db, target_date=record_in.date)
        match = next((r for r in roster if r.student_id == record_in.student_id), None)
        if match:
            return match
        return schemas.AttendanceRecordOut(
            id=saved.id,
            student_id=saved.student_id,
            room_id=saved.room_id,
            date=saved.date,
            status=saved.status,
            notes=saved.notes,
            student_name=saved.student.name if saved.student else "Student",
            roll_number=saved.student.roll_number if saved.student else None,
            room_number=saved.room.room_number if saved.room else "N/A",
            block=saved.room.block if saved.room else "N/A",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/bulk", response_model=dict)
def mark_bulk_attendance(
    bulk_in: schemas.AttendanceBulkMark,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Bulk mark an entire block or the whole hostel with a designated status.
    """
    count = crud.bulk_mark_attendance(
        db,
        target_date=bulk_in.date,
        block=bulk_in.block,
        status=bulk_in.status,
        marked_by=current_user.id,
    )
    return {
        "message": f"Successfully updated attendance for {count} residents.",
        "count": count,
    }


@router.get("/export")
def export_attendance_csv(
    date_str: Optional[str] = Query(None, alias="date"),
    block: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Export the roll call register as a downloadable CSV.
    Matches the 'Export CSV' button in C9 Hostelos_image4.jpeg.
    """
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    roster = crud.get_attendance_roster(db, target_date=target_date, block=block)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Block", "Room Number", "Roll Number", "Student Name", "Status", "Notes"])

    for r in roster:
        writer.writerow([r.date.isoformat(), r.block, r.room_number, r.roll_number or "N/A", r.student_name, r.status, r.notes or ""])

    csv_data = output.getvalue()
    filename = f"hostelos_attendance_{target_date.isoformat()}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
