import json
import csv
import urllib2
import model
import operator
from haversine import distance
from jinja2 import Template
from flask import Flask, render_template, request
from model import session as dbsession

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/report", methods = ['POST'])
def lookup():
	l = request.form['lat']
	g = request.form['long']
# function 1. Take lat long form input from user (main.html):
# Iterate through stations.latitude, stations.longitude and use haversine function to find closest stations
#  closest stations that are reporting, and where snow depth > 0.
	dist_list = []
	for counter in range(1, 868):
		s = dbsession.query(model.Station).get(counter)
		try: 
			s.snow_data[0]
			u = s.snow_data[0]
			print s.id, s.given_id, s.latitude, s.longitude, u.sta_given_id, u.depth, u.depth_change
			origin = float(l), float(g)
			destination = float(s.latitude), float(s.longitude)
			kms = int(distance(origin, destination))
			mi = int(0.621371*kms)
			if u.depth > 0:
				dist_list.append({'dist':mi, 'id':s.given_id, 'depth':u.depth, 'depth_change':u.depth_change})
		except IndexError:
			print s.id, s.given_id, s.latitude, s.longitude
			origin = 34.134115, -118.321548
			destination = s.latitude, s.longitude
			kms = int(distance(origin, destination))
			mi = int(0.621371*kms)
	closest_sta = sorted(dist_list, key=lambda k: k['dist'])[0:10]
	# Return the 10 closest stations, their distances away in miles (converted from kms)
	#  and basic telemetry data for that station
	for locations in closest_sta:
		print 'The', locations.get('id'), 'station is', locations.get('dist'), 'miles away. There are', locations.get('depth'), "inches of snow there."
	return render_template ("report.html", closest_sta = closest_sta, lat = l, lng = g)
	
	# Next:
	# Make this better - look at 5 stations (or radius?), if no snow, look at next 5 closest stations (or wider radius).
	#  or take radius input.
	# Write function for returning deepest snow (range?)
	# Write function for returning newest snow (range?)
	# Write function for returning best snow quality (based on water_equiv)

if __name__ == "__main__":
    app.run(debug = True)
