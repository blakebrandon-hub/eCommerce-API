from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean


Base = declarative_base()


class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	public_id = Column(String)
	username = Column(String)
	email = Column(String(80))
	password = Column(String)
	admin = Column(Boolean)


class Product(Base):
	__tablename__ = 'products'
	id = Column(Integer, primary_key=True)
	product_id = Column(String)
	user_id = Column(String)
