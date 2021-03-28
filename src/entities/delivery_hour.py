import datetime
import sqlalchemy
from sqlalchemy import orm
from src.db_session import SqlAlchemyBase


class DeliveryHour(SqlAlchemyBase):
    __tablename__ = 'delivery_hours'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    start = sqlalchemy.Column(sqlalchemy.Time)
    end = sqlalchemy.Column(sqlalchemy.Time)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"))

    order = orm.relation("Order")

    def set_delivery_hour(self, delivery_hour: str):
        begin, end = delivery_hour.split('-')
        hours, minutes = map(int, begin.split(':'))
        self.start = datetime.time(hour=hours, minute=minutes)
        hours, minutes = map(int, end.split(':'))
        self.end = datetime.time(hour=hours, minute=minutes)

    @property
    def delivery_hour(self):
        return f"{self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"
