import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase


class Region(SqlAlchemyBase):
    __tablename__ = 'regions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    region_number = sqlalchemy.Column(sqlalchemy.Integer)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("couriers.id"))

    courier = orm.relation("Courier")
