"""
=============================================================================
HOSTELOS - LEAVE & GATE PASS ROUTER (routers/leaves.py)
=============================================================================
API endpoints for:
  - Applying for Out-station Leaves / Gate Passes (Weekend outing, Emergency, Vacation)
  - Approval workflows (Pending -> Approved -> Validated / Checked Out)
  - Pass Code tracking (GP-2026-XXXX)
=============================================================================
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, models, crud
from ..auth import get_current_user, get_optional_current_user, get_current_warden_or_admin

router = APIRouter(prefix="/leaves", tags=["Leaves & Gate Passes"])


@router.get("", response_model=List[schemas.LeaveOut])
def list_leave_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    leave_type: Optional[str] = Query(None),
    only_mine: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Optional[Any] = Depends(get_optional_current_user),
):
    """
    Query gate passes.
    Enforces Role-Based Access:
    - Students can ONLY view their own gate passes.
    - Wardens and Admins can view and authorize all student passes.
    """
    if current_user and current_user.role == models.UserRole.STUDENT.value:
        student_id = current_user.id
    elif only_mine and current_user:
        student_id = current_user.id
    else:
        student_id = None

    leaves = crud.get_leave_requests(
        db,
        student_id=student_id,
        status=status_filter,
        leave_type=leave_type,
        skip=skip,
        limit=limit,
    )

    out_list = []
    for l in leaves:
        out_list.append(
            schemas.LeaveOut(
                id=l.id,
                pass_code=l.pass_code,
                student_id=l.student_id,
                leave_type=l.leave_type,
                departure_date=l.departure_date,
                return_date=l.return_date,
                destination=l.destination,
                reason=l.reason,
                emergency_contact=l.emergency_contact,
                parent_consent=l.parent_consent,
                status=l.status,
                approved_by=l.approved_by,
                created_at=l.created_at,
                student=schemas.UserSummary.model_validate(l.student) if l.student else None,
            )
        )
    return out_list


@router.post("", response_model=schemas.LeaveOut, status_code=status.HTTP_201_CREATED)
def apply_leave(
    leave_in: schemas.LeaveCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Resident submits an out-station leave or gate pass request.
    Matches C9 Hostelos_image7.jpeg (Out-Station Leave Application Form).
    """
    if getattr(current_user, "role", None) != models.UserRole.STUDENT.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can apply for out-station gate passes. Authorities and admins review and approve passes.",
        )

    leave = crud.create_leave_request(db, leave_in, student_id=current_user.id)
    full_leave = crud.get_leave_by_id(db, leave.id)
    return schemas.LeaveOut(
        id=full_leave.id,
        pass_code=full_leave.pass_code,
        student_id=full_leave.student_id,
        leave_type=full_leave.leave_type,
        departure_date=full_leave.departure_date,
        return_date=full_leave.return_date,
        destination=full_leave.destination,
        reason=full_leave.reason,
        emergency_contact=full_leave.emergency_contact,
        parent_consent=full_leave.parent_consent,
        status=full_leave.status,
        approved_by=full_leave.approved_by,
        created_at=full_leave.created_at,
        student=schemas.UserSummary.model_validate(full_leave.student) if full_leave.student else None,
    )


@router.get("/{leave_id}", response_model=schemas.LeaveOut)
def get_leave_detail(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[Any] = Depends(get_optional_current_user),
):
    """Fetch gate pass details, verifying student ownership."""
    l = crud.get_leave_by_id(db, leave_id)
    if not l:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")

    if current_user and current_user.role == models.UserRole.STUDENT.value:
        if l.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own leave requests.",
            )

    return schemas.LeaveOut(
        id=l.id,
        pass_code=l.pass_code,
        student_id=l.student_id,
        leave_type=l.leave_type,
        departure_date=l.departure_date,
        return_date=l.return_date,
        destination=l.destination,
        reason=l.reason,
        emergency_contact=l.emergency_contact,
        parent_consent=l.parent_consent,
        status=l.status,
        approved_by=l.approved_by,
        created_at=l.created_at,
        student=schemas.UserSummary.model_validate(l.student) if l.student else None,
    )


@router.patch("/{leave_id}/status", response_model=schemas.LeaveOut)
def update_leave_status(
    leave_id: int,
    status_update: schemas.LeaveStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Warden or Institute Head authorizes, validates, or rejects a pass.
    """
    try:
        updated = crud.update_leave_status(db, leave_id, status_update.status, approver_id=current_user.id)
        return get_leave_detail(updated.id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
