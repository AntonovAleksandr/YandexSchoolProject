import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from .delivery_hour import DeliveryHour


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    weight = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    region_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    delivery_hours = orm.relation("DeliveryHour", back_populates='order')

    is_taken = sqlalchemy.Column(sqlalchemy.Integer, default=False)

    def update_delivery_hours(self, hours, session):
        session.query(DeliveryHour).filter(DeliveryHour.order_id == self.id).delete()
        for i in hours:
            hour = DeliveryHour(courier_id=self.courier_id)
            hour.set_delivery_hour(i)
            session.add(hour)
        session.commit()
