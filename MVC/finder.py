import os
import json
import csv
import urllib2
import model
from alerts import load_alert
import operator
from twilio.rest import TwilioRestClient
from haversine import distance
from jinja2 import Template
from sqlalchemy import desc
from sqlalchemy import select
from sqlalchemy.sql.expression import func
from sqlalchemy import Table, Column, Float, Integer, Boolean, String, MetaData, ForeignKey
from flask import Flask, render_template, request, make_response, session
from model import session as dbsession

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

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
	session["location"] = {"input":(l,g)}
	print l, g
	# Iterate through stations.latitude, stations.longitude and use haversine function to find closest stations
	#  closest stations that are reporting, and where snow depth > 0.
	#  ...this is so slow. How can I make it faster?  --> Geospatial database, different algorithm
	dist_list = []
	s = dbsession.query(model.Station).all()
	for counter in s:
		try: 
			u = counter.snow_data[-1]
			origin = float(l), float(g)
			destination = float(counter.latitude), float(counter.longitude)
			kms = int(distance(origin, destination))
			mi = int(0.621371*kms)
			if u.depth != None and u.depth > 0:
				if u.water_equiv != None and u.water_equiv != 0:
					density = (int((u.water_equiv / u.depth) * 100))
					if density > 100:
							density = 100
				else: 
					density = "No Data" 
				dist_list.append({'dist':mi, 'id':counter.given_id, 'ele':counter.elevation, 'lat':counter.latitude, 'lng':counter.longitude, 'name':counter.name, 'depth':u.depth,\
				'depth_change':u.depth_change, 'density':density})
			else:
				continue
		except IndexError:
			continue
	# Return the 10 closest stations, their distances away in miles (converted from kms)
	#  and basic telemetry data for that station
	closest_sta = sorted(dist_list, key=lambda k: k['dist'])[0:10]
	response = json.dumps({"closest": closest_sta})
	return response

	# Next:
	# Make this better - look at 5 stations (or radius?), if no snow, look at next 5 closest stations (or wider radius).
	#  or take radius input.
	# Return best snow quality (based on density, temp, depth)

@app.route("/see_all", methods = ['GET','POST'])
def see_all():
	button = request.values.get("button", 0, type=int)
	if button == 1:
		all_depth = []
		s = dbsession.query(model.Station).all()
		for counter in s:
			try: 
				u = counter.snow_data[-1]
				if u.depth != None and u.depth > 0:
					all_depth.append({'lat': counter.latitude, 'lng': counter.longitude, 'name':counter.name, 'depth':u.depth})
				else:
					continue
			except IndexError:
				print "Index Error exception triggered"
		print all_depth
		response = json.dumps(all_depth)
		return response

@app.route("/charts", methods = ['GET','POST'])
def charts():
	station_name = request.args.get("station")
	print station_name
	result = dbsession.query(model.Station).filter_by(name=station_name).one()
	# print result.id
	# trend_data = dbsession.query(model.Snow_Data).filter_by(station_id=result.id)
	# print trend_data[-7:]
	u = []
	u = result.snow_data[-7:]
	chart_data = []
	for item in u:
		if item.water_equiv != None and item.water_equiv != 0:
			if item.depth == 0:
				density = 0
			else:
				density = int((item.water_equiv / item.depth) * 100)
				if density > 100:
					density = 100
		else:
			density = 0
		chart_data.append({"date":item.date.strftime("%m/%d/%y"),"depth":item.depth,"station":station_name,"density":density})
	print chart_data
	chart_data = json.dumps(chart_data)
	return chart_data
	
@app.route("/alert", methods = ['GET','POST'])
def alert():
	from_number = request.values.get('From')
	station = request.values.get('Body')
	client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
	number_to_text = from_number
	station_alert = dbsession.query(model.Station).get(station)
	if int(station) > 0 and int(station) < 868:
		# Send confirmation message and send alert info to alerts table:
		hello = "You set an alert for station: %s!  We'll let you know when that station registers new snow!" % (station_alert.name)
		message = client.messages.create(from_=TWILIO_NUMBER,
									to=number_to_text,
									body=hello)
		load_alert(from_number, station)
	else:
		# invalid input handling - need upstream scrub for text entries.
		hello = "%s is an invalid station number, please try again!" % (station)
	return "Alert sent"

if __name__ == "__main__":
    app.run(debug = True)