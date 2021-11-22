from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
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
    authorization = Column(String(100))

    def __repr__(self):
        return f"{self.id}, {self.Firstname}, {self.Lastname}, {self.properties}, {self.authorization} "


class Class(Base):
    __tablename__ = "Class"
    id = Column(Integer, primary_key=True)
    adress = Column(String(45))
    name = Column(String(45))
    class_user = Column(Integer, ForeignKey("User.id"), nullable=False)
    info = Column(String(200))
    User = relationship("User")

    def __repr__(self):
        return f"{self.id}, {self.adress}, {self.name}, {self.class_user}"


#  alembic revision --autogenerate -m "Initial migration."
# alembic upgrade head
class Book(Base):
    __tablename__ = "Book"
    id = Column(Integer, primary_key=True)
    classId = Column(Integer, ForeignKey("Class.id"), nullable=False)
    StartDateTime = Column(DATETIME)
    ENDDateTime = Column(DATETIME)
    book_user = Column(Integer, ForeignKey("User.id"), nullable=False)

    User = relationship("User")
    Class = relationship("Class")

    def __repr__(self):
        return f"{self.id}, {self.classId}, {self.StartDateTime}, {self.ENDDateTime}, {self.booked},{self.book_user} "
