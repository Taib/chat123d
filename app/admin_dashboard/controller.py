import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_guard import get_librarian_active_user
from app.admin_dashboard.repository_dashboard import DashboardRepository
from app.admin_dashboard.repository_weekly import (
    DashboardWeeklyRepository,
    get_week_number,
)


dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_librarian_active_user)],
)


@dashboard_router.get(
    "/main",
    status_code=status.HTTP_200_OK,
)
async def get_dashboard(repo: DashboardRepository = Depends()):
    """
    Get main dashboard.
    """
    try:
        return repo.get_dashboard()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@dashboard_router.get(
    "/weekly",
    status_code=status.HTTP_200_OK,
)
async def get_weekly_dashboard(
    week: int = Query(get_week_number(), minimum=1, maximum=53),
    year: int = Query(datetime.datetime.today().year, minimum=2000, maximum=2025),
    repo: DashboardWeeklyRepository = Depends(),
):
    """
    Get weekly dashboard.
    """
    try:
        return repo.get_dashboard_by_week(week, year)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@dashboard_router.get(
    "/weekly/all",
    status_code=status.HTTP_200_OK,
)
async def get_all_weekly_dashboards(
    repo: DashboardWeeklyRepository = Depends(),
):
    """
    Get all weekly dashboards.
    """
    try:
        return repo.get_all_weekly_dashboards()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
