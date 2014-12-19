import os
import json
import model
from alerts import load_alert
import operator
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

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', '378fj339802h&^*!^&^A0Zr98j/3yX R~XHH!jmN]LWX/,?RT')

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
	# Check if location is in Alaska. If in Alaska, search Alaska stations.
	if l > 54:
		# Alaska
		stations = dbsession.query(model.Station).filter(model.Station.latitude > 54)
	# Check if location is north of 45 degrees latitude.  If so, search north of 40 degrees.
	if 54 > l > 45:
		stations = dbsession.query(model.Station).filter(54 > model.Station.latitude > 40)
	else:
	# Search a slice of the continental US based on longitudinal partitions
		if g < -120:
			stations = dbsession.query(model.Station).filter(model.Station.longitude < -115)
		if -120 < g < -115:
			stations = dbsession.query(model.Station).filter(-125 < model.Station.longitude < -110)
		if -115 < g < -110:
			stations = dbsession.query(model.Station).filter(-120 < model.Station.longitude < -105)
		if -110 < g < -105:
			stations = dbsession.query(model.Station).filter(-115 < model.Station.longitude < -100)
		if g > -105: 
			stations = dbsession.query(model.Station).filter(-110 < model.Station.longitude)
	dist_list = []
	for station in stations:
		try: 
			snow = station.snow_data[-1]
			origin = float(l), float(g)
			destination = float(station.latitude), float(station.longitude)
			kms = int(distance(origin, destination))
			mi = int(0.621371*kms)
			if snow.depth != None and snow.depth > 0:
				if snow.water_equiv != None and snow.water_equiv != 0:
					density = (int((snow.water_equiv / snow.depth) * 100))
					if density > 100:
							density = 100
				else: 
					density = "No Data" 
				dist_list.append({'dist':mi, 'text-code':station.id, 'id':station.given_id, 'ele':station.elevation,\
					'lat':station.latitude, 'lng':station.longitude, 'name':station.name, 'depth':snow.depth,\
				'depth_change':snow.depth_change, 'density':density, 'date':snow.date.strftime("%m/%d/%y %H:%M")})
			else:
				continue
		except IndexError:
			continue
	# Return the 10 closest stations, their distances away in miles (converted from kms)
	#  and basic telemetry data for that station
	closest_sta = sorted(dist_list, key=lambda k: k['dist'])[0:10]
	time_stamps = [x['date'] for x in closest_sta]
	time_stamp = max(time_stamps)
	response = json.dumps({"closest": closest_sta, "time_stamp":time_stamp})
	return response

@app.route("/see_all", methods = ['GET','POST'])
def see_all():
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
    app.run(debug = False)
