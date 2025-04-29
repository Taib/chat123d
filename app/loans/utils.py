from datetime import datetime
from app.loans.models import Loan


def get_week_number(date: datetime | None = None) -> int:
    """
    Return the ISO week number for the given date.
    If no date is provided, use today's date.
    """
    if date is None:
        date = datetime.today()
    return date.isocalendar()[1]


def post_loan_creation_process(loan: Loan):
    from app.db.sql.base_engine import base_session
    from app.admin_dashboard.repository_dashboard import DashboardRepository
    from app.admin_dashboard.repository_weekly import DashboardWeeklyRepository

    with base_session() as session:
        dash_repo = DashboardRepository(session)
        dash_weekly_repo = DashboardWeeklyRepository(session)
        # update dashboard
        dash_repo.increment_dashboard(
            dashboard_id="admin_dashboard",
            field="total_loans",
            increment=1,
        )
        # update weekly dashboard
        dash_weekly_repo.increment_dashboard_by_week(
            week_number=get_week_number(),
            year=datetime.today().year,
            field="total_loans",
            increment=1,
        )
        # TODO: add logic to update most borrowed book
        # TODO: add logic to update most borrowed author
