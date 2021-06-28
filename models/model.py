from datetime import date, datetime as dt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    Date,
    DateTime,
    Float,
    ForeignKey
)


engine = create_engine("sqlite:////Users/tolikdemchuk/PycharmProjects/PracticeGal/data.db", future=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


# All for films
class Company(Base):
    __tablename__ = "Company"

    id = Column(Integer, primary_key=True)
    name = Column("Name", String(50), nullable=False, unique=True)


class Category(Base):
    __tablename__ = "Category"

    id = Column(Integer, primary_key=True)
    name = Column("Name", String(50), nullable=False, unique=True)


class Sales(Base):
    __tablename__ = "Sales"

    id = Column(Integer, primary_key=True)
    film_id = Column("Film id", Integer, ForeignKey("Film.id"))
    peoples = Column("Peoples", Integer, nullable=False, default=0)
    ticket_price = Column("Ticket", Float, nullable=False)


class Dates(Base):
    __tablename__ = "Dates"

    id = Column(Integer, primary_key=True)
    film_id = Column("Film Id", Integer, ForeignKey("Film.id"))
    start_date = Column("Start", Date, nullable=False)
    end_date = Column("End", Date, nullable=False)


class Film(Base):
    __tablename__ = "Film"

    id = Column(Integer, primary_key=True)
    name = Column("Name", String(100), nullable=False)
    description = Column("Description", String(256), nullable=False)
    company_id = Column("Company Id", Integer, ForeignKey("Company.id"))
    category_id = Column("Category Id", Integer, ForeignKey("Category.id"))
    release_date = Column("Release", DateTime, default=dt.utcnow)
    active = Column("Active", Boolean, default=True)
    sales = relationship("Sales", uselist=False, backref="Film")
    dates = relationship("Dates", uselist=False, backref="Film")


# All for users
class Users(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True)
    username = Column("Username", String(16), unique=True, nullable=False)
    full_name = Column("Full Name", String(100), nullable=False)
    email = Column("Email", String(50), nullable=False, unique=True)
    hashed_password = Column("Hashed pass", String(512), nullable=False)
    salts = relationship("Salts", uselist=False, backref="Users")
    perm = relationship("Perm", uselist=False, backref="Users")
    dates = relationship("RegDates", uselist=False, backref="Users")


class Salts(Base):
    __tablename__ = "Salts"

    id = Column(Integer, primary_key=True)
    user_id = Column("User Id", Integer, ForeignKey("Users.id"))
    salt = Column("Salt", String(50), nullable=False)


class Perm(Base):
    __tablename__ = "Perm"

    id = Column(Integer, primary_key=True)
    user_id = Column("User Id", Integer, ForeignKey("Users.id"))
    admin = Column("Admin", Boolean, default=False)


class RegDates(Base):
    __tablename__ = "RegDates"

    id = Column(Integer, primary_key=True)
    user_id = Column("User Id", Integer, ForeignKey("Users.id"))
    reg_date = Column("Register", Date, default=date.today)
    last_activity = Column("Last Act", Date, nullable=True, default=date.today)


Base.metadata.create_all(engine)
