#!/usr/bin/env python
import json
import csv
import urllib2
import datetime

# This script is the daily chron job to call the api for each station, and save the parsed JSON data into a file.

def parse_cron():
	# Open a new csv file, and add headers
	utc_datetime = datetime.datetime.utcnow()
	formatted_string = utc_datetime.strftime("%Y-%m-%d-%H%MZ") 
	filename = '/Users/pieradamonte/Dropbox/Hackbright/HBProject/Outputs/SnowDataParsed%s.csv' % formatted_string
	f = csv.writer(open(filename, 'w'))
	f.writerow(['source', 'name', 'triplet', 'elevation', 'wind', 'timezone', 'lat', 'lng', 'date', 'depth', 'depth_change', 'water_equiv', 'water_equiv_change'])
	# Open the URLs for the API calls, call the API, and iterate over the resultant JSON
	with open('/Users/pieradamonte/Dropbox/Hackbright/HBProject/Cron/APIurls.csv', 'rb') as csvfile:
		snow_reader = csv.reader(csvfile)
		writer = csv.writer(open(filename, 'wb'))
		for row in snow_reader:
			req = urllib2.Request(row[0])
			response = urllib2.urlopen(req)
			data = json.load(response)
	# Parse the JSON and save the parsed JSON into a new file
			if data['data'] != []:
				source = 'SNOTEL'
				name = data['station_information']['name']
				triplet = data['station_information']['triplet']
				elevation = data['station_information']['elevation']
				wind = data['station_information']['wind']
				timezone = (data['station_information']['timezone'])
				lat = float(data['station_information']['location']['lat'])
				lng = float(data['station_information']['location']['lng'])
				date = data['data'][0]['Date']
				depth = data['data'][0]['Snow Depth (in)']
				depth_change = data['data'][0]['Change In Snow Depth (in)']
				water_equiv = data['data'][0]['Snow Water Equivalent (in)']
				water_equiv_change = data['data'][0]['Change In Snow Water Equivalent (in)']
				row = [source, name, triplet, elevation, wind, timezone, lat, lng, date, depth, depth_change, water_equiv, water_equiv_change]
				print row
				f.writerow(row)
	# Some of the entries do not have data points, and for these, enter None
			else:
				source = 'SNOTEL'
				name = data['station_information']['name']
				triplet = data['station_information']['triplet']
				elevation = data['station_information']['elevation']
				wind = data['station_information']['wind']
				timezone = data['station_information']['timezone']
				lat = float(data['station_information']['location']['lat'])
				lng = float(data['station_information']['location']['lng'])
				date = None
				depth = None
				depth_change = None
				water_equiv = None
				water_equiv_change = None
				row = [source, name, triplet, elevation, wind, timezone, lat, lng, date, depth, depth_change, water_equiv, water_equiv_change]
				print row
				f.writerow(row)

def main():
	parse_cron()
    
if __name__ == "__main__":
	main()
