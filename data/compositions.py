import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class MainTable(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'main'
    Manufacturer = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    #Name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    Product = sqlalchemy.Column(sqlalchemy.String)
    Price = sqlalchemy.Column(sqlalchemy.Integer)
    Min_quantity = sqlalchemy.Column(sqlalchemy.Integer)
    Type = sqlalchemy.Column(sqlalchemy.String)
    Rating_sum = sqlalchemy.Column(sqlalchemy.Integer)
    Rating_count = sqlalchemy.Column(sqlalchemy.Integer)
    Rating_avg = sqlalchemy.Column(sqlalchemy.Float)



    def print_name(self):
        return self.Name

    def __repr__(self):
        return f'<User>{self.Name}'
