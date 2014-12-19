import os
import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, String, DateTime, Boolean

# ENGINE = create_engine("sqlite:///Snow.db", echo = False)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///pieradamonte')
# DATABASE_URL = 'postgresql:///pieradamonte'
ENGINE = create_engine(DATABASE_URL, echo = False)
session = scoped_session(sessionmaker(bind=ENGINE, autocommit = False, autoflush = False)) 
Base = declarative_base()

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key = True)
    source = Column(String(15), nullable = False)
    name = Column(String(50), nullable = True)
    given_id = Column(String(20), nullable = True)
    latitude = Column(Float, nullable = False)
    longitude = Column (Float, nullable = False)
    elevation = Column(Integer, nullable = False)
    wind = Column(Boolean(50), unique=False)
    timezone = Column(Integer, nullable = True)

class Snow_Data(Base):
    __tablename__ = "snow_data"

    id = Column(Integer, primary_key = True)
    station_id = Column(Integer, ForeignKey('stations.id'))
    sta_given_id = Column(String(25), nullable=True)
    source = Column(String(25), nullable = False)
    units = Column(String(10), nullable = False)
    date = Column(DateTime, nullable = False)
    depth = Column(Integer, nullable = False)
    depth_change = Column(Integer, nullable = True)
    water_equiv = Column(Float, nullable = True)
    water_equiv_change = Column(Float, nullable = True)
    station = relationship("Station", backref=backref("snow_data", order_by=id))

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey('stations.id'))
    phone_number = Column(String(30), nullable = False)
    status = Column(Boolean(50), unique=False)
    station = relationship("Station", backref=backref("alerts", order_by=id))

def add_data():
    global ENGINE
    global Session

    # ENGINE = create_engine("sqlite:///Snow.db", echo = True)
    # DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///pieradamonte')
    ENGINE = create_engine(DATABASE_URL, echo = False)
    Session = scoped_session(sessionmaker(bind=ENGINE, autocommit = False, autoflush = False)) 

    session = Session()
    return Session()

def create_tables():
    global ENGINE
    global Session

    # ENGINE = create_engine("sqlite:///Snow.db", echo = True)
    # DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///localhost')
    ENGINE = create_engine(DATABASE_URL, echo = False)
    Session = sessionmaker(bind=ENGINE)
    Base.metadata.create_all(ENGINE)

    return Session()

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
    