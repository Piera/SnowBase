#!/usr/bin/env python
import json
import csv
import urllib2
import io
import datetime
# import requests

# This script is the daily chron job to call the api for each station, and save the JSON data into a file.
#  This uses URLs created by running 1) create_station_json.py and 2) create_urls.py

utc_datetime = datetime.datetime.utcnow()
formatted_string = utc_datetime.strftime("%Y-%m-%d-%H%MZ") 
filename = '/Users/pieradamonte/Dropbox/Hackbright/HBProject/Outputs/SnowDataJSON%s.csv' % formatted_string
with io.open(filename, 'w') as f:
	with open('/Users/pieradamonte/Dropbox/Hackbright/HBProject/Cron/APIurls.csv', 'rb') as csvfile:
		snow_reader = csv.reader(csvfile)
		for row in snow_reader:
			# When using requests:
			# res = requests.get(row[0])
			# data = res.json()
			req = urllib2.Request(row[0])
			response = urllib2.urlopen(req)
			# Changed the line below to make data a list for easier parsing. Moved 11.6.2014 cron job out of Outputs file.
			# Subsequent cron job outputs - 11.7.2014 and on have data in lists
			data = [json.load(response)]
			print data
			f.write(unicode(json.dumps(data)))


