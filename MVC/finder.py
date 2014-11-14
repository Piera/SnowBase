import json
import csv
import urllib2
import model
import operator
from haversine import distance
from jinja2 import Template
from sqlalchemy import desc
from flask import Flask, render_template, request, make_response, session
from model import session as dbsession

app = Flask(__name__)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/report", methods = ['GET','POST'])
def lookup():
	# From Google maps API:
	l = request.values.get("lat", 0, type=float)
	g = request.values.get("lng", 0, type=float)
	print l, g
	# Iterate through stations.latitude, stations.longitude and use haversine function to find closest stations
	#  closest stations that are reporting, and where snow depth > 0.
	dist_list = []
	s = dbsession.query(model.Station).all()
	for counter in s:
		try: 
			u = counter.snow_data[-1]
			# use if not != None... or [] -- try/except can hide other errors!
			origin = float(l), float(g)
			destination = float(counter.latitude), float(counter.longitude)
			kms = int(distance(origin, destination))
			mi = int(0.621371*kms)
			if u.depth != None and u.depth > 0:
				# print s.id, s.given_id, s.name, s.latitude, s.longitude, u.sta_given_id,\
				#  u.depth, u.depth_change, u.date
				dist_list.append({'dist':mi, 'id':counter.given_id, 'lat': counter.latitude, 'lng': counter.longitude, 'name':counter.name, 'depth':u.depth,\
				 'depth_change':u.depth_change})
			else:
				continue
		except IndexError:
			origin = 34.134115, -118.321548
			destination = counter.latitude, counter.longitude
			kms = int(distance(origin, destination))
			mi = int(0.621371*kms)
	closest_sta = sorted(dist_list, key=lambda k: k['dist'])[0:10]
	print "Closest stations: ", closest_sta
	deepest_snow = sorted(closest_sta, key=lambda k: k['depth'], reverse=True)[0:10]
	print "Deepest snow: ", deepest_snow
	most_new_snow = sorted(closest_sta, key=lambda k: k['depth_change'], reverse=True)[0:10]
	print "Most new snow: ", most_new_snow

	# Return the 10 closest stations, their distances away in miles (converted from kms)
	#  and basic telemetry data for that station
	for locations in closest_sta:
		# print 'The', locations.get('name'), 'station is', locations.get('dist'), 'miles away. There are',\
		#  locations.get('depth'), "inches of snow there."
		session["l"] = {"input":(locations.get('lat'), locations.get('lng'))}
	# response = make_response(render_template('report_singlepage.html', closest_sta=closest_sta))
	response = json.dumps({"closest": closest_sta, "deepest": deepest_snow, "most new": most_new_snow})
	# print type(response)
	return response

	# Next:
	# Make this better - look at 5 stations (or radius?), if no snow, look at next 5 closest stations (or wider radius).
	#  or take radius input.
	# Return best snow quality (based on water_equiv)

if __name__ == "__main__":
    app.run(debug = True)