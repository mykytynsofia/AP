import os
import random
from datetime import datetime
# from dateutil.relativedelta import relativedelta
# from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
# from models import Book
# from models import Class

engine = create_engine('mysql://root:mysqlpass@127.0.0.1/audience')
connection = engine.connect()

Session = sessionmaker(bind=engine)
session = Session()

# for n in range(1,6):
#     object = User(id=n, name='user_name', username='user_username',
#               password='*****')
#     print(f"Adding user{n}.")
#     session.add(object)
#
# for n in range(1,10):
#     object = Tickets(id=n, row='1', place='2',
#               namefilm='film',datatime = '2020-01-01 00:00:00',reservation = 'yes',buy = 'no')
#     print(f"Adding ticket{n}.")
#     session.add(object)

# for n in range(1,7):
#     object = Buy(id=n, name='name', idticket='1',
#              )
#     print(f"Adding buy{n}.")
#     session.add(object)

session.commit()
