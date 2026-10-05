"""
=============================================================================
HOSTELOS - COMPLAINT MANAGEMENT ROUTER (routers/complaints.py)
=============================================================================
API endpoints for:
  - Filing infrastructure/maintenance complaints (Plumbing, Electrical, Internet, etc.)
  - Querying and filtering complaint records (CM-2026-XXXX)
  - Resolving tickets and assigning technicians
=============================================================================
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, models, crud
from ..auth import get_current_user, get_optional_current_user, get_current_warden_or_admin

router = APIRouter(prefix="/complaints", tags=["Complaints"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=List[schemas.ComplaintOut])
def list_complaints(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    urgency: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    only_mine: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Optional[Any] = Depends(get_optional_current_user),
):
    """
    Query complaints with relational data.
    Enforces Role-Based Access:
    - Students can ONLY see their own filed complaints.
    - Wardens and Admins can access all complaints across all blocks.
    """
    if current_user and current_user.role == models.UserRole.STUDENT.value:
        student_id = current_user.id
    elif only_mine and current_user:
        student_id = current_user.id
    else:
        student_id = None

    complaints = crud.get_complaints(
        db,
        student_id=student_id,
        status=status_filter,
        category=category,
        urgency=urgency,
        search=search,
        skip=skip,
        limit=limit,
    )

    out_list = []
    for c in complaints:
        out_list.append(
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
        )
    return out_list


@router.post("", response_model=schemas.ComplaintOut, status_code=status.HTTP_201_CREATED)
def file_complaint(
    complaint_in: schemas.ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Resident registers a new maintenance ticket.
    Matches root_screenshot.png (Register Complaint Form).
    """
    try:
        complaint = crud.create_complaint(db, complaint_in, student_id=current_user.id)
        # Reload with relationships
        full_complaint = crud.get_complaint_by_id(db, complaint.id)
        return schemas.ComplaintOut(
            id=full_complaint.id,
            ticket_number=full_complaint.ticket_number,
            student_id=full_complaint.student_id,
            room_id=full_complaint.room_id,
            category=full_complaint.category,
            title=full_complaint.title,
            description=full_complaint.description,
            urgency=full_complaint.urgency,
            status=full_complaint.status,
            assigned_staff=full_complaint.assigned_staff,
            resolution_notes=full_complaint.resolution_notes,
            image_url=full_complaint.image_url,
            created_at=full_complaint.created_at,
            resolved_at=full_complaint.resolved_at,
            student=schemas.UserSummary.model_validate(full_complaint.student) if full_complaint.student else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/upload", response_model=dict)
def upload_complaint_image(
    file: UploadFile = File(...),
    current_user: Any = Depends(get_current_user),
):
    """Upload photo/attachment for maintenance complaint."""
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".jpg", ".jpeg", ".png", ".webp", ".pdf"]:
        raise HTTPException(status_code=400, detail="Allowed file types: JPG, PNG, WEBP, PDF")

    filename = f"complaint_{uuid.uuid4().hex[:12]}{file_ext}"
    dest_path = UPLOAD_DIR / filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"image_url": f"/uploads/{filename}"}


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[Any] = Depends(get_optional_current_user),
):
    """Fetch complaint details by ID, verifying student ownership."""
    c = crud.get_complaint_by_id(db, complaint_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint ticket not found")

    if current_user and current_user.role == models.UserRole.STUDENT.value:
        if c.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own complaints.",
            )

    return schemas.ComplaintOut(
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


@router.patch("/{complaint_id}/status", response_model=schemas.ComplaintOut)
def update_status(
    complaint_id: int,
    update_in: schemas.ComplaintUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Warden or Institute Head resolves ticket, assigns staff or escalates.
    """
    try:
        updated = crud.update_complaint_status(db, complaint_id, update_in)
        return get_complaint(updated.id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
