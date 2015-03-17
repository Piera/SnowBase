import os
import json
import model
import heapq
import psycopg2
from alerts import load_alert
import operator
import geohash
from twilio.rest import TwilioRestClient
from haversine import distance
from jinja2 import Template
from sqlalchemy.sql.expression import func
from sqlalchemy import Table, Column, Float, Integer, Boolean, String, MetaData, ForeignKey, desc, select
from flask import Flask, render_template, request, make_response, session
from model import session as dbsession

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')
# DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql:///localhost')

app = Flask(__name__)

SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', '378fj339802h&^*!^&^A0Zr98j/3yX R~XHH!jmN]LWX/,?RT')
app.config['SECRET_KEY'] = SECRET_KEY

@app.route("/")
def index():
	return render_template("main.html")

@app.route("/report", methods = ['GET','POST'])
def lookup():
	"""Calculate ten closest stations from input latitude and longitude, return data for ten closest stations as a JSON object."""

	# From Google maps API:
	l = request.values.get("lat", 0, type=float)
	g = request.values.get("lng", 0, type=float)
	session["location"] = {"input":(l,g)}
	# Geohash encode the input, then determine the expanded neighborhood based on expanded geohash
	reference_location = geohash.encode(l, g)
	location_box = geohash.expand(reference_location[:3])
	neighborhoods = []
	for place in location_box:
		geohash_str = place + '%'
		neighbor = dbsession.query(model.Station_Geohash).\
			select_from(model.Station_Geohash).\
			filter(model.Station_Geohash.geohash_loc.ilike(geohash_str)).\
			all()
		neighborhoods = neighborhoods + neighbor
	dist_list = []
	# For all of the stations found in neighborhoods, check for data and snow. 
	# If there is data and snow for a given station, add it to the heap
	for location in neighborhoods:
		try: 
			station = dbsession.query(model.Station).filter(model.Station.id == location.station_id).one()
			snow = station.snow_data[-1]
			if snow.depth != None and snow.depth > 0:
				origin = float(l), float(g)
				destination = float(station.latitude), float(station.longitude)
				kms = int(distance(origin, destination))
				mi = int(0.621371*kms)
				heapq.heappush(dist_list, (mi, station.id))
			else:
				continue
		except IndexError:
			continue
	# Return the 10 closest stations, their distances away in miles (converted from kms)
	#  and basic telemetry data for that station
	closest_sta = [heapq.heappop(dist_list) for i in range(10)]
	responses_list = []
	for station in closest_sta:
		mi = station[0]
		station = dbsession.query(model.Station).filter(model.Station.id == station[1]).one()
		snow = station.snow_data[-1]
		if snow.water_equiv != None and snow.water_equiv != 0:
			density = (int((snow.water_equiv / snow.depth) * 100))
			if density > 100:
				density = 100
			if density == None:
				density = "No Data" 
		responses_list.append({'dist':mi, 'text-code':station.id, 'id':station.given_id, 'ele':station.elevation,\
				'lat':station.latitude, 'lng':station.longitude, 'name':station.name, 'depth':snow.depth,\
				'depth_change':snow.depth_change, 'density':density, 'date':snow.date.strftime("%m/%d/%y %H:%M")})

	time_stamps = [x['date'] for x in responses_list]
	time_stamp = max(time_stamps)
	response = json.dumps({"closest": responses_list, "time_stamp":time_stamp})
	return response

@app.route("/see_all", methods = ['GET','POST'])
def see_all():
	"""Return snow depth data for all stations."""
	# See all functionality - returns all of the snow data to view in one heatmap
	see_all = request.values.get("see_all", 0, type=int)
	if see_all:
		all_depth = []
		stations = dbsession.query(model.Station).all()
		for station in stations:
			try: 
				snow = station.snow_data[-1]
				if snow.depth != None and snow.depth > 0:
					all_depth.append({'lat': station.latitude, 'lng': station.longitude, 'name':station.name, 'depth':snow.depth})
				else:
					continue
			except IndexError:
				print "Index Error exception triggered"
		response = json.dumps(all_depth)
		return response

@app.route("/charts", methods = ['GET','POST'])
def charts():
	"""Get telemetry data for station input from chart, return data as a JSON object"""
	# With station name, return data to create d3 charts in display
	station_name = request.args.get("station")
	station = dbsession.query(model.Station).filter_by(name=station_name).one()
	snow = []
	snow = station.snow_data[-7:]
	chart_data = []
	for reading in snow:
		if reading.water_equiv != None and reading.water_equiv != 0:
			if reading.depth == 0:
				density = 0
			else:
				density = int((reading.water_equiv / reading.depth) * 100)
				if density > 100:
					density = 100
		else:
			density = 0
		chart_data.append({"date":reading.date.strftime("%m/%d/%y"),"depth":reading.depth,"station":station_name,"density":density,\
			"lat":station.latitude,"lng":station.longitude})
	chart_data = json.dumps(chart_data)
	return chart_data
	
@app.route("/alert", methods = ['GET','POST'])
def alert():
	"""
	Check if values from text message input are valid integers, send error text message if invalid, set alert and send confirmation if valid.
	
	Error text triggers:
	input < 0
	input > 868
	int(string) ValueError 
	"""

	print request.values
	from_number = request.values.get('From')
	station = request.values.get('Body')
	client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
	number_to_text = from_number

	try:
		station = int(station)
		if station > 0 and station < 868:
	# Send confirmation message and send alert info to alerts table:
			station_alert = dbsession.query(model.Station).get(station)
			alert_text = "You set an alert for station: %s!  We'll let you know when that station registers new snow!" % (station_alert.name)
			message = client.messages.create(from_=TWILIO_NUMBER,
										to=number_to_text,
										body=alert_text)
			load_alert(from_number, station)
		else:
	# Invalid input handling:
			error_text = "%s is an invalid station number, please try again!" % (station)
			message = client.messages.create(from_=TWILIO_NUMBER,
										to=number_to_text,
										body=error_text)
	
	except ValueError: 
		error_text = "%s is an invalid entry, please use station code!" % (station)
		message = client.messages.create(from_=TWILIO_NUMBER,
										to=number_to_text,
										body=error_text)
	return "Alert sent"

if __name__ == "__main__":
	PORT = int(os.environ.get("PORT", 5000))
	DEBUG = "NO_DEBUG" not in os.environ
	app.run(debug = DEBUG, port=PORT, host="0.0.0.0")
