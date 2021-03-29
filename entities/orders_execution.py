import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from properties import DEFAULT_COMPLETE_TIME


class OrderExecution(SqlAlchemyBase):
    __tablename__ = 'orders_execution'

    orders_execution_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"))
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.id"))
    assign_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    complete_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    delivery_time = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    order = orm.relation("Order")
    courier = orm.relation("Courier")

    def set_delivery_time(self, session):
        prev = session.query(OrderExecution).filter(OrderExecution.courier_id == self.courier_id,
                                                    OrderExecution.complete_time != DEFAULT_COMPLETE_TIME,
                                                    OrderExecution.complete_time <= self.complete_time,
                                                    OrderExecution.order_id != self.order_id).all()
        if prev:
            mx = max(prev, key=lambda s: s.complete_time)
            time_diff = self.complete_time - mx.complete_time
        else:
            time_diff = self.complete_time - self.assign_time
        self.delivery_time = time_diff.seconds + time_diff.days * 3600 * 24
        print()