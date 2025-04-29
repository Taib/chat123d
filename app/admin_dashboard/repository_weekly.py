from fastapi import Depends
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.get_db import get_db
from app.db.sql.base_repository import BaseRepository
from app.db.sql.utils import pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from app.admin_dashboard.entities import DashboardWeeklyEntity
from app.admin_dashboard.models import DashboardWeekly, DashboardWeeklySave

import logging
logger = logging.getLogger("liboo.app.admin_dashboard.repository_dashboard")

def dashboard_weekly_entity_to_model(entity: DashboardWeeklyEntity) -> DashboardWeekly:
    """
    Convert a DashboardWeeklyEntity to a model.
    """
    return sqlalchemy_to_pydantic(entity, DashboardWeekly, exclude={"password"})


def dashboard_weekly_model_to_entity(model: DashboardWeekly) -> DashboardWeeklyEntity:
    """
    Convert a model to a DashboardWeeklyEntity.
    """
    return pydantic_to_sqlalchemy(model, DashboardWeeklyEntity, exclude_unset=True)


def get_week_number(date: datetime.datetime | None = None) -> int:
    """
    Return the ISO week number for the given date.
    If no date is provided, use today's date.
    """
    if date is None:
        date = datetime.datetime.today()
    return date.isocalendar()[1]


class DashboardWeeklyRepository(BaseRepository[DashboardWeeklyEntity]):
    def __init__(
        self,
        session: Session = Depends(get_db),
    ):
        super().__init__(DashboardWeeklyEntity, session)

    def get_all_weekly_dashboards(self) -> list[DashboardWeekly]:
        """
        Get all dashboard.
        """
        dashboard = self.query().all()
        return [dashboard_weekly_entity_to_model(dashboard) for dashboard in dashboard]

    def get_dashboard_by_week(
        self,
        week: int | None = get_week_number(),
        year: int | None = datetime.datetime.today().year,
    ) -> DashboardWeekly | None:
        """
        Get a dashboard by week.
        """
        logger.debug(f"Fetching dashboard for week: {week}, year: {year}")
        dashboard = self.query().filter_by(week=week, year=year).first()
        if dashboard:
            return dashboard_weekly_entity_to_model(dashboard)
        return None

    def create_dashboard(self, dashboard: DashboardWeeklySave) -> DashboardWeekly:
        """
        Create a new dashboard.
        """

        try:
            entity = dashboard_weekly_model_to_entity(dashboard)
            result = self.create(entity)
            return dashboard_weekly_entity_to_model(result)
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            raise ValueError("dashboard-creation-failed")

    def update_dashboard(self, dashboard: DashboardWeeklySave) -> DashboardWeekly:
        """
        Update an existing dashboard.
        """
        existing = self.get_dashboard_by_week(
            week=dashboard.week,
            year=dashboard.year,
        )
        if not existing:
            raise ValueError("dashboard-not-found")

        self.update(existing.id, dashboard.model_dump(exclude_unset=True))
        return self.find_by_id(dashboard.id)

    def delete_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete a dashboard by ID.
        """
        self.delete(dashboard_id)
        return True

    def increment_dashboard_by_week(
        self,
        week_number: int = get_week_number(),
        year: int = datetime.datetime.today().year,
        field: str = "total_loans",
        increment: int = 1,
    ) -> DashboardWeekly:
        """
        Increment a field in the dashboard.
        """
        if not self.get_dashboard_by_week(week=week_number, year=year):
            self.create_dashboard(
                DashboardWeeklySave(
                    week=week_number,
                    year=year,
                    total_loans=0,
                )
            )
        self.session.execute(
            text(
                f"""
            UPDATE {DashboardWeeklyEntity.__tablename__}
            SET {field} = {field} + :increment
            WHERE week = :week_number AND year = :year
            """
            ),
            {"increment": increment, "week_number": week_number, "year": year},
        )
        self.session.commit()
        return self.get_dashboard_by_week(week=week_number, year=year)
