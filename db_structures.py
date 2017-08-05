from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config

"""
Here we define the relevant backend DB structures that will hold the sales data etc.
"""

Base = declarative_base()

# Class to hold the categories of items
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, default='', nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    relative_position = Column(Integer, default=0, nullable=False)

# Class to hold the categories of items
class SubCategory(Base):
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key=True)
    name = Column(String, default='', nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    description = Column(String, default='')

# class that holds a single session of recording
class SaleSession(Base):
    __tablename__ = 'sale_sessions'
    id = Column(Integer, primary_key=True)
    time_opened = Column(DateTime, nullable=False)

    # override the string representation
    def __str__(self):
        return '<SaleSession %s @%s>' % (self.id, self.time_opened)
    __repr__ = __str__

# Class which sales will be connected to
class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    sale_time = Column(DateTime, nullable=False)
    session_id = Column(Integer, ForeignKey('sale_sessions.id'))

# A sale class, representing a sold item
class SaleItem(Base):
    __tablename__ = 'sale_items'
    id = Column(Integer, primary_key=True)                          #Primary Key
    sale_id = Column(Integer, ForeignKey('sales.id'))               #Sale this belongs to
    category_id = Column(Integer, ForeignKey('categories.id'))      #Category of the item
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'))#Subcategory of the item
    price =  Column(Float, default=0.0, nullable=False)             #Price the item was sold for

# user class for holding aspects about the users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    real_name = Column(String, default='', nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    points = Column(Float, default=0)
    special_points = Column(Float, default=0)
    raised = Column(Float, default=0)
    # privileges = Column()

# class to hold the user logs
class UserLog(Base):
    __tablename__ = 'user_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    logged_in = Column(Boolean, nullable=False)
    time = Column(DateTime, nullable=False)

# function we will use to create a session and engine
def init_database():
    engine = create_engine('sqlite:///pos_db.sqlite')
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    # try getting the debug value to see if we add the dummmy data
    if config.settings.get('debug', False) and config.settings.get('dummy', False):
        dummy_data(session)

    # return the session object for use in the app engine
    return session

# purely for debugging purposes
def dummy_data(session):
    import datetime
    s = session()

    cats = [Category(name='books', relative_position=0), Category(name='clothes',relative_position=1)]

    for c in cats:
        s.add(c)

    s.commit()

    subcats = [SubCategory(name='fiction', category_id=cats[0].id)]

    for sc in subcats:
        s.add(sc)

    s.add(User(real_name='Aaron Tranter', username='aaron', password='testo', salt='1'))

    # s.add(SaleSession(time_opened=datetime.datetime.now()))
    # s.add(SaleSession(time_opened=datetime.datetime.now()))

    s.commit()

    q = s.query(Category).all()
    # print [o.name for o in q]