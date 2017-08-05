from db_structures import *
import datetime
from tools import logger

"""
In this file will go any functions that operate on the database like adding objects etc.
"""

def open_sales(session):
    # get the current date so we can filter
    today = datetime.date.today()

    # create a query to see what the sessions are, get any with a date >= than today
    q = session.query(SaleSession).filter(SaleSession.time_opened >= today).all()

    if len(q) >= 1:
        logger('Found session(s) %s. Using latest.' % str(q))
        sale_session = q[-1]
    else:
        logger('No sessions found. Opening new session.')

        # create a new session and commit it
        sale_session = SaleSession(time_opened=datetime.datetime.now())
        session.add(sale_session)
        session.commit()

        logger('Opened new session: %s' % str(sale_session))

    # return the sale session object
    return sale_session

# load the categories from the database
def get_categories(session):
    cat_query = session.query(Category).all()

    return cat_query

# load the subcategories from the database
def get_subcategories(session):
    subcat_query = session.query(SubCategory).all()

    return subcat_query

# get a list of users from the DB
def get_users(session):
    user_query = session.query(User).all()

    return user_query