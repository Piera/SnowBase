#!/usr/bin/env python
import json
import csv
import urllib2
import model
from model import Station, Snow_Data
from scan import alert_scan
from datetime import datetime
from sqlalchemy import Table, Column, Float, Integer, Boolean, String, MetaData, ForeignKey

# Fill the database of snow data with daily telemetry data points
def load_snow_data(session):
	print "Session!"
	telemetry_data = None
# 1. Open the list of URLs for the API calls, iterate the API calls
	# with open('/Users/pieradamonte/Dropbox/Hackbright/HBProject/Cron/APIurls.csv', 'rb') as csvfile:
	with open('Project/Cron/APIurls.csv', 'rb') as csvfile:
		print "CSV Opened!!"
		snow_reader = csv.reader(csvfile)
		for row in snow_reader:
			print "Reading rows in csv"
			req = urllib2.Request(row[0])
			response = urllib2.urlopen(req)
			snow_data = json.load(response)
# 2. Parse the resultant JSON and add the parsed JSON directly into the Snow.db snow_data table
			# Check to see if there is data
			if snow_data['data'] != [] and snow_data['data'][0]['Date'] != None:
				print "There is data, now checking for snow depth"

				# Check to see if there is snow depth data point
				if snow_data['data'][0]['Snow Depth (in)'] != None:
					# If there is snow depth data, proceed with data addition or update
					triplet = snow_data['station_information']['triplet']
					station_id = session.query(model.Station).filter_by(given_id=triplet).one()
					entries = session.query(model.Snow_Data).filter_by(station_id=station_id.id).order_by(model.Snow_Data.date).all()
					# entries = session.query(model.Snow_Data).filter_by(station_id=station_id.id).all()
					print entries

					# What if there are no snow data entries for the station? Create a new one.
					if not entries:
						print "EXCEPT"
						source = 'SNOTEL'
						units = 'in'
						date = datetime.now()
						depth = int(snow_data['data'][0]['Snow Depth (in)'])
						depth_change = None
						water_equiv = None
						water_equiv_change = None
						if snow_data['data'][0]['Change In Snow Depth (in)'] != None:
							depth_change = int(snow_data['data'][0]['Change In Snow Depth (in)'])
						if snow_data['data'][0]['Snow Water Equivalent (in)'] != None:
							water_equiv = float(snow_data['data'][0]['Snow Water Equivalent (in)'])
						if snow_data['data'][0]['Change In Snow Water Equivalent (in)'] != None:
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
						print "Adding telemetry data, inside the EXCEPT."

					# Otherwise: Compare the dates; if date is the same, update the database
					elif entries and datetime.date(entries[-1].date) == datetime.date(datetime.now()):
						print datetime.date(entries[-1].date)
						last_entry = entries[-1]
						# datetime.date(last_entry.date) == datetime.date(datetime.now())
						# last_entry = entries[-1]
						print "Dates are same: update data"
						last_entry.source = 'SNOTEL'
						last_entry.units = 'in'
						last_entry.date = datetime.now()
						last_entry.depth = int(snow_data['data'][0]['Snow Depth (in)'])
						depth_change = None
						water_equiv = None
						water_equiv_change = None
						if snow_data['data'][0]['Change In Snow Depth (in)'] != None:
							last_entry.depth_change = int(snow_data['data'][0]['Change In Snow Depth (in)'])
						if snow_data['data'][0]['Snow Water Equivalent (in)'] != None:
							last_entry.water_equiv = float(snow_data['data'][0]['Snow Water Equivalent (in)'])
						if snow_data['data'][0]['Change In Snow Water Equivalent (in)'] != None:
							last_entry.water_equiv_change = float(snow_data['data'][0]['Change In Snow Water Equivalent (in)'])
						if depth_change != None:
							last_entry.depth_change = depth_change
						if water_equiv != None:
							last_entry.water_equiv = water_equiv
						if water_equiv_change != None:
							last_entry.water_equiv_change = water_equiv_change
						session.commit()
						print "Committing data where dates are same"

					# If the dates are different, then create a new entry in the database
					else:
						print "Dates are different, adding a datapoint"
						print datetime.date(entries[-1].date)
						source = 'SNOTEL'
						units = 'in'
						date = datetime.now()
						depth = int(snow_data['data'][0]['Snow Depth (in)'])
						depth_change = None
						water_equiv = None
						water_equiv_change = None
						if snow_data['data'][0]['Change In Snow Depth (in)'] != None:
							depth_change = int(snow_data['data'][0]['Change In Snow Depth (in)'])
						if snow_data['data'][0]['Snow Water Equivalent (in)'] != None:
							water_equiv = float(snow_data['data'][0]['Snow Water Equivalent (in)'])
						if snow_data['data'][0]['Change In Snow Water Equivalent (in)'] != None:
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
						print "Adding telemetry data, inside the else."
						session.add(telemetry_data)
		session.commit()
		print "COMMIT at end of parsing and everything"

def main(session):
	load_snow_data(session)
	alert_scan(session)
    
if __name__ == "__main__":
    s = model.add_data()
    main(s)
    