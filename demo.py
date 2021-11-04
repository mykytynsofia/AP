from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
engine = create_engine('mysql://root:chornobai2002@localhost:3306/bd')
connection = engine.connect()

Session = sessionmaker(bind=engine)
session = Session()

for n in range(1,10):
    object = User(id=n, Firstname='user_Firstname', Lastname='user_Lastname',
              properties='ALL',authorization='1111')
    print(f"Adding user{n}.")
    session.add(object)


session.commit()