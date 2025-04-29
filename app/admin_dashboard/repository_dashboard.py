from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.get_db import get_db
from app.db.sql.base_repository import BaseRepository
from app.db.sql.utils import pydantic_to_sqlalchemy, sqlalchemy_to_pydantic
from app.admin_dashboard.entities import DashboardEntity
from app.admin_dashboard.models import Dashboard, DashboardUpdate

import logging
logger = logging.getLogger("liboo.app.admin_dashboard.repository_dashboard")


def dashboard_entity_to_model(entity: DashboardEntity) -> Dashboard:
    """
    Convert a DashboardEntity to a model.
    """
    return sqlalchemy_to_pydantic(entity, Dashboard, exclude={"password"})


def dashboard_model_to_entity(model: Dashboard) -> DashboardEntity:
    """
    Convert a model to a DashboardEntity.
    """
    return pydantic_to_sqlalchemy(model, DashboardEntity, exclude_unset=True)


class DashboardRepository(BaseRepository[DashboardEntity]):
    def __init__(
        self,
        session: Session = Depends(get_db),
    ):
        super().__init__(DashboardEntity, session)

    def get_dashboard(self, dashboard_id: str = "admin_dashboard") -> Dashboard | None:
        """
        Get a dashboard by ID.
        """
        logger.info(f"Fetching dashboard with ID: {dashboard_id}")
        dashboard = self.find_by_id(dashboard_id)
        logger.info(f"Dashboard found: {dashboard}")
        if dashboard:
            return dashboard_entity_to_model(dashboard)
        return None

    def increment_dashboard(
        self,
        dashboard_id: str = "admin_dashboard",
        field: str = "total_loans",
        increment: int = 1,
    ) -> Dashboard:
        """
        Increment a field in the dashboard.
        """
        self.session.execute(
            text(
                f"""
            UPDATE {DashboardEntity.__tablename__}
            SET {field} = {field} + :increment
            WHERE id = :dashboard_id
            """,
            ),
            {"increment": increment, "dashboard_id": dashboard_id},
        )
        self.session.commit()
        return self.get_dashboard(dashboard_id)

    def update_dashboard(self, dashboard: DashboardUpdate) -> Dashboard:
        """
        Update an existing dashboard.
        """
        self.update(dashboard.id, dashboard.model_dump(exclude_unset=True))
        return self.find_by_id(dashboard.id)
