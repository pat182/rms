from ...model import RestaurantTable, User, RestaurantUser, Restaurant
from ...model.repositories.restaurant_table_repo import RestaurantTableRepo
from ...schemas.restaurant import CreateRestoRequest

# from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class RestaurantTableService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.repo = RestaurantTableRepo(self.db)
        self.model = self.repo.model

    async def create_resto_table(
            self,restaurant: Restaurant,
            payload:list[CreateRestoRequest],
    )-> list[RestaurantTable]:

        resto_tables : list[RestaurantTable] = []

        for resto in payload:

            resto_table = self.model(
                restaurant_id=restaurant.id,
                table_name=resto.table_name,
                capacity=resto.capacity,
                is_active=True
            )
            resto_tables.append(resto_table)

        self.db.add_all(resto_tables)

        await self.db.flush()

        return resto_tables
