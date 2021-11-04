from sqlalchemy import Column,  ForeignKey, Integer, String,Boolean
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    Firstname = Column(String(45), nullable=False)
    Lastname = Column(String(45), nullable=False)
    properties = Column(String(45))
    authorization = Column(String(45))


class Book(Base):
    __tablename__ = "Book"
    id = Column(Integer, primary_key=True)
    classId = Column(Integer)
    StartDateTime = Column(DATETIME)
    ENDDateTime = Column(DATETIME)
    booked = Column(Boolean)
    iduser = Column(Integer,ForeignKey('User.id'))
    users = relationship("User")

class Buy(Base):
    __tablename__ = "Class"
    id = Column(Integer, primary_key=True)
    adress = Column(String(45))
    name = Column(String(45))
