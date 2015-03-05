#!/usr/bin/env python
import model
import geohash
from model import session
from sqlalchemy import Table, Column, Float, Integer, Boolean, String, MetaData, ForeignKey

def seed_geohashed_station_database(session):
	stations = session.query(model.Station).all()
	for station in stations:
		geohash_loc = geohash.encode(station.latitude, station.longitude)
		station_geohash = model.Station_Geohash(\
			station_id = station.id,\
			geohash_loc = geohash_loc)
		session.add(station_geohash)
	session.commit()

def main(session):
	seed_geohashed_station_database(session)
    
if __name__ == "__main__":
    s= model.create_tables()
    main(s)

