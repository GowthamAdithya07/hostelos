"""
=============================================================================
HOSTELOS - ROOMS & BED ALLOCATION ROUTER (routers/rooms.py)
=============================================================================
API endpoints for:
  - Querying room capacity and live occupancy across Blocks A, B, and C
  - Visual bed status inspection (🔴 Occupied / 🟢 Vacant)
  - Bed allocation and checkout/deallocation
=============================================================================
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, models, crud
from ..auth import get_current_user, get_current_warden_or_admin

router = APIRouter(prefix="/rooms", tags=["Rooms & Allocation"])


@router.get("", response_model=List[schemas.RoomOut])
def get_all_rooms(
    block: Optional[str] = Query(None, description="Filter by Block (Block A, Block B, Block C)"),
    room_type: Optional[str] = Query(None, description="Filter by Room Type (Single, Double)"),
    has_ac: Optional[bool] = Query(None, description="Filter by AC status"),
    search: Optional[str] = Query(None, description="Search by room number or student name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Retrieve hostel rooms with live bed occupancy breakdown.
    Matches C9 Hostelos_image2.jpeg.
    """
    return crud.get_rooms(
        db,
        block=block,
        room_type=room_type,
        has_ac=has_ac,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get("/students/unallocated", response_model=List[schemas.UserSummary])
def get_unallocated_students(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """Fetch all resident students currently unallocated (room_id IS NULL)."""
    students = crud.get_students(db, search=search, unallocated_only=True)
    return students


@router.get("/students/all", response_model=List[schemas.UserSummary])
def get_all_students(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Fetch all students for selection/search."""
    students = crud.get_students(db, search=search, unallocated_only=False)
    return students


@router.get("/{room_id}", response_model=schemas.RoomOut)
def get_room_details(room_id: int, db: Session = Depends(get_db)):
    """Fetch room entity by primary key with occupants."""
    room = crud.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    occ_list = [
        schemas.UserSummary(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            roll_number=u.roll_number,
            room_number=room.room_number,
            block=room.block,
        )
        for u in room.occupants
    ]
    occupied_count = len(occ_list)
    vacant_count = max(0, room.capacity - occupied_count)
    beds = [
        schemas.BedStatus(
            bed_index=i + 1,
            is_occupied=i < occupied_count,
            student=occ_list[i] if i < occupied_count else None,
        )
        for i in range(room.capacity)
    ]

    return schemas.RoomOut(
        id=room.id,
        room_number=room.room_number,
        block=room.block,
        room_type=room.room_type,
        capacity=room.capacity,
        has_ac=room.has_ac,
        created_at=room.created_at,
        occupants=occ_list,
        occupied_count=occupied_count,
        vacant_count=vacant_count,
        beds=beds,
    )


@router.post("", response_model=schemas.RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(
    room_in: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """Create a new room in a hostel block."""
    existing = crud.get_room_by_number(db, room_in.room_number.strip().upper())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room {room_in.room_number} already exists in the system.",
        )
    created = crud.create_room(db, room_in)
    return get_room_details(created.id, db)


@router.post("/allocate", response_model=schemas.UserSummary)
def allocate_student_to_room(
    alloc_data: schemas.AllocateBedRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Allocate a student to a room bed. Enforces capacity checks and Foreign Key integrity.
    """
    try:
        updated_student = crud.allocate_bed(db, alloc_data.room_id, alloc_data.student_id)
        return schemas.UserSummary.model_validate(updated_student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/deallocate", response_model=schemas.UserSummary)
def deallocate_student_from_room(
    alloc_data: schemas.AllocateBedRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_warden_or_admin),
):
    """
    Vacate bed / checkout student from assigned room. Sets student.room_id to NULL.
    """
    try:
        updated_student = crud.deallocate_bed(db, alloc_data.student_id)
        return schemas.UserSummary.model_validate(updated_student)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
