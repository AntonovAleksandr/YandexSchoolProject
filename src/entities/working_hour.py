import datetime
import sqlalchemy
from sqlalchemy import orm
from src.db_session import SqlAlchemyBase


class WorkingHour(SqlAlchemyBase):
    __tablename__ = 'working_hours'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    start = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    end = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.id"))

    courier = orm.relation("Courier")

    def set_working_hour(self, working_hour: str):
        begin, end = working_hour.split('-')
        self.start = datetime.time(*map(int, begin.split(':')))
        self.end = datetime.time(*map(int, end.split(':')))

    @property
    def working_hour(self):
        return f"{self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"
