from sqlalchemy.orm import selectinload

from app.core.base_repo import BaseRepo

from sqlalchemy import select

from app.model import RestaurantTable, DiningSession


class RestaurantTableRepo(BaseRepo):
    SEARCH_FIELDS = ("table_name",)
    SORT_FIELDS = ("table_name", "created_at", "updated_at")
    
    @property
    def model(self):
        return RestaurantTable

    async def get_by_id_with_sesh(self, _id: int,restaurant_id) -> RestaurantTable | None:
        stmt = (
            select(self.model)
            .where(
                self.model.id == _id,
                self.model.restaurant_id == restaurant_id,
            )
            .options(
                selectinload(
                    self.model.dining_sessions.and_(
                        DiningSession.status.in_(["verified", "pending"])
                    )
                )
            )
        )

        return await self.db.scalar(stmt)

    async def get_dinning_sesh(self, session_token: str) -> DiningSession | None:
        sesh = (await self.db.execute(
            select(DiningSession)
            .where(DiningSession.session_token == session_token)
        ))

        return sesh.scalar_one_or_none()

    def apply_custom_sorting(self, stmt, sort_by, sort_order):
        if sort_by == "has_active_session":
            has_active_session = (
                select(DiningSession.id)
                .where(
                    DiningSession.restaurant_table_id == self.model.id,
                    DiningSession.is_active.is_(True),
                    DiningSession.closed_at.is_(None),
                )
                .exists()
            )

            return stmt.order_by(
                has_active_session.asc()
                if sort_order == "asc"
                else has_active_session.desc()
            )

        return stmt
