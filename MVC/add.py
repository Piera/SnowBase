#!/usr/bin/env python
import json
import csv
import ast # Converts "True" and "False" to boolean values
import urllib2
import model
from model import Snow_Data
from datetime import datetime
from sqlalchemy import Table, Column, Float, Integer, Boolean, String, MetaData, ForeignKey

# Fill the database of snow data with daily telemetry data points
def load_snow_data(session):
# 1. Open the list of URLs for the API calls, iterate the API calls
	with open('/Users/pieradamonte/Dropbox/Hackbright/HBProject/Cron/APIurls.csv', 'rb') as csvfile:
		snow_reader = csv.reader(csvfile)
		for row in snow_reader:
			req = urllib2.Request(row[0])
			response = urllib2.urlopen(req)
			snow_data = json.load(response)
# 2. Parse the resultant JSON and add the parsed JSON directly into the Snow.db snow_data table
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
	load_snow_data(session)
    
if __name__ == "__main__":
    s= model.add_data()
    main(s)