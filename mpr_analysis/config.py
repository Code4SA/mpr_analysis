import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_URI = os.environ.get('DB_URI', 'postgres://mpr@localhost/mpr')


def get_session():
    engine = create_engine(DB_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
