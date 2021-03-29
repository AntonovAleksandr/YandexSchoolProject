import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from entities.orders_execution import OrderExecution
from entities.region import Region
from entities.working_hour import WorkingHour
from properties import DEFAULT_COMPLETE_TIME, COEFFICIENT


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    regions = orm.relation("Region", back_populates='courier')
    working_hours = orm.relation("WorkingHour", back_populates='courier')
    orders = orm.relation("OrderExecution", back_populates='courier')

    def update_regions(self, regions, session):
        session.query(Region).filter(Region.courier_id == self.id).delete()
        for i in regions:
            session.add(Region(region_number=i, courier_id=self.id))
        session.commit()

    def update_working_hours(self, hours, session):
        session.query(WorkingHour).filter(WorkingHour.courier_id == self.id).delete()
        for i in hours:
            hour = WorkingHour(courier_id=self.id)
            hour.set_working_hour(i)
            session.add(hour)
        session.commit()

    def get_rating(self, session):
        average_times = []
        regions = [i.region_number for i in self.regions]
        for i in regions:
            length = len(session.query(OrderExecution).filter(OrderExecution.courier_id == self.id,
                                                              OrderExecution.complete_time != DEFAULT_COMPLETE_TIME).all())
            average = 0
            next_time = 0
            for j in range(1, length + 1):
                complete_order = session.query(OrderExecution).filter(OrderExecution.courier_id == self.id,
                                                                      OrderExecution.complete_time != DEFAULT_COMPLETE_TIME).all()[
                    j - 1]
                end = (complete_order.complete_time.hour * 60 + complete_order.complete_time.minute) * 60 + \
                      complete_order.complete_time.second
                if j == 1:
                    start = (complete_order.assign_time.hour * 60 + complete_order.assign_time.minute) * 60 + \
                            complete_order.assign_time.second
                    next_time = end
                else:
                    start = next_time
                    next_time = end
                diff = abs(end - start)
                average = ((j - 1) * average + diff) // j
            average_times.append(average)

        return (60 * 60 - min(min(average_times), 60 * 60)) / (60 * 60) * 5

    def get_earning(self, session):
        earning = 0
        complete_orders = session.query(OrderExecution).filter(OrderExecution.courier_id == self.id,
                                                               OrderExecution.complete_time != DEFAULT_COMPLETE_TIME).all()
        for order in complete_orders:
            earning = earning + 500 * COEFFICIENT[order.courier.type]
        return earning
