"""
=============================================================================
HOSTELOS - OPERATIONS ANALYTICS & METRICS ROUTER (routers/analytics.py)
=============================================================================
API endpoints for:
  - Aggregated KPI cards: Total Occupancy (78%), Active Complaints (10),
    Pending Leaves (4), Attendance Today (90%)
  - Recent complaints and approved gate passes
  - Matches C9 Hostelos_image1.png
=============================================================================
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud
from ..auth import get_optional_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics & Overview"])


@router.get("/overview", response_model=schemas.DashboardMetricsOut)
def get_operations_overview(
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """
    Fetch comprehensive KPI metrics for the Executive Operations Dashboard.
    Matches C9 Hostelos_image1.png.
    """
    return crud.get_dashboard_metrics(db, current_user=current_user)
