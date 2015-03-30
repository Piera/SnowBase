#!/usr/bin/env python
"""
seed.py

Seed db tables with Stations data, snow telemetry data from csv file, 
	snow telemetry data from Powderlin.es API urls.
"""

import json
import csv
import ast # Converts "True" and "False" to boolean values
import urllib2
import model
from datetime import datetime
from sqlalchemy import Table, Column, Float, Integer, Boolean, String, MetaData, ForeignKey

# Seed the database of stations from a CSV file:
def load_stations(session):
    with open('SnowDataParsed2014-11-08-0152Z.csv') as csvfile:
        station_file = csv.reader(csvfile, delimiter = ',')
        for station in station_file:
            source = station[0]
            name = station[1]
            given_id = station[2]
            latitude = float(station[6])
            longitude = float(station[7])
            elevation = int(station[3])
            wind = ast.literal_eval(station[4])
            timezone = station[5]
            station = model.Station(\
             	source = source,\
             	name = name,\
             	given_id = given_id,\
             	latitude = latitude,\
             	longitude = longitude,\
             	wind = wind, \
             	elevation= elevation,\
            	timezone=timezone)
            session.add(station)
        session.commit()

# Seed the database of snow data from a CSV file:
def load_snow_data_csv(session):
	with open('/Users/pieradamonte/Dropbox/Hackbright/HBProject/Outputs/SnowDataParsed2014-11-24-0721Z.csv') as csvfile:
		snow_reader = csv.reader(csvfile, delimiter = ',')
		for snow_data in snow_reader: 
			if snow_data[8]:
				if  snow_data[9] != None and snow_data[9] != '':
					triplet = snow_data[2]
					station_id = session.query(model.Station).filter_by(given_id=triplet).one()
					source = 'SNOTEL'
					units = 'in'
					date = datetime.strptime(snow_data[8], '%Y-%m-%d')
					depth = int(snow_data[9])
					if snow_data[10] != None and snow_data[10] != '':
						depth_change = int(snow_data[10])
					if snow_data[11] != None and snow_data[11] != '':
						water_equiv = float(snow_data[11])
					if snow_data[12] != None and snow_data[12] != '':
						water_equiv_change = float(snow_data[12])
					telemetry_data = model.Snow_Data(\
						sta_given_id = triplet,\
						station_id = station_id.id,\
						source = source,\
						units = units,\
						date = date,\
						depth = depth)
					if depth_change != None:
						telemetry_data.depth_change = depth_change
					if water_equiv != None:
						telemetry_data.water_equiv = water_equiv
					if water_equiv_change != None:
						telemetry_data.water_equiv_change = water_equiv_change
			session.add(telemetry_data)
		session.commit()


# Seed the database of snow data (daily telemetry data points) from API:
def load_snow_data_API(session):
# 1. Open the list of URLs for the API calls, iterate the API calls
	with open('/Users/pieradamonte/Dropbox/Hackbright/HBProject/Cron/APIurls_short.csv', 'rb') as csvfile:
		snow_reader = csv.reader(csvfile)
		for row in snow_reader:
			req = urllib2.Request(row[0])
			response = urllib2.urlopen(req)
			snow_data = json.load(response)
# 2. Parse the resultant JSON and seed the parsed JSON directly into the Snow.db snow_data table
			if snow_data['data'] != [] and snow_data['data'][0]['Date'] != None:
				if snow_data['data'][0]['Snow Depth (in)'] != None:
					triplet = snow_data['station_information']['triplet']
					station_id = session.query(model.Station).filter_by(given_id=triplet).one()
					source = 'SNOTEL'
					units = 'in'
					date = datetime.strptime(snow_data['data'][0]['Date'], '%Y-%m-%d')
					depth = int(snow_data['data'][0]['Snow Depth (in)'])
					if snow_data['data'][0]['Change In Snow Depth (in)'] != None:
						depth_change = int(snow_data['data'][0]['Change In Snow Depth (in)'])
					if snow_data['data'][0]['Snow Water Equivalent (in)'] != None:
						water_equiv = float(snow_data['data'][0]['Snow Water Equivalent (in)'])
					if snow_data['data'][0]['Change In Snow Water Equivalent (in)'] !=None:
						water_equiv_change = float(snow_data['data'][0]['Change In Snow Water Equivalent (in)'])
					telemetry_data = model.Snow_Data(\
						sta_given_id = triplet,\
						station_id = station_id.id,\
						source = source,\
						units = units,\
						date = date,\
						depth = depth)
					if depth_change != None:
						telemetry_data.depth_change = depth_change
					if water_equiv != None:
						telemetry_data.water_equiv = water_equiv
					if water_equiv_change != None:
						telemetry_data.water_equiv_change = water_equiv_change
			session.add(telemetry_data)
		session.commit()

def main(session):
	# load_stations(session)
	load_snow_data_csv(session)
	# load_snow_data_API(session)
    
if __name__ == "__main__":
    s= model.create_tables()
    main(s)
