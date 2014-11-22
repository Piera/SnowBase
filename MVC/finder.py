import os
import json
import csv
import urllib2
import model
import operator
from twilio.rest import TwilioRestClient
from haversine import distance
from jinja2 import Template
from sqlalchemy import desc
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
				dist_list.append({'dist':mi, 'id':counter.given_id, 'ele':counter.elevation, 'lat': counter.latitude, 'lng': counter.longitude, 'name':counter.name, 'depth':u.depth,\
				 'depth_change':u.depth_change})
			else:
				continue
		except IndexError:
			origin = 34.134115, -118.321548
			destination = counter.latitude, counter.longitude
			kms = int(distance(origin, destination))
			mi = int(0.621371*kms)
	closest_sta = sorted(dist_list, key=lambda k: k['dist'])[0:10]
	# print "Closest stations: ", closest_sta
	deepest_snow = sorted(closest_sta, key=lambda k: k['depth'], reverse=True)[0:2]
	# print "Deepest snow: ", deepest_snow
	most_new_snow = sorted(closest_sta, key=lambda k: k['depth_change'], reverse=True)[0:2]
	# print "Most new snow: ", most_new_snow

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

@app.route("/see_all", methods = ['GET','POST'])
def see_all():
	button = request.values.get("button", 0, type=int)
	if button == 1:
		all_depth = []
		s = dbsession.query(model.Station).all()
		for counter in s:
			try: 
				u = counter.snow_data[-1]
				# use if not != None... or [] -- try/except can hide other errors!
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
	u = []
	u = result.snow_data[-7:]
	print 
	chart_data = []
	for item in u:
		chart_data.append({"date":item.date.strftime("%m/%d/%y"),"depth":item.depth})
	print chart_data
	chart_data = json.dumps(chart_data)
	return chart_data
	

@app.route("/alert", methods = ['GET','POST'])
def alert():
# Getting Twilio working, and sending test text messages
	status = request.values.get("alert", 0, type=int)
	station = request.values.get("station", 0, type=int)
	if status == 1:
		client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
		number_to_text = "+1510phone#"
		station = dbsession.query(model.Station).first()
		print station.name
		depth = station.snow_data[-1].depth
		print depth
		depth_change = station.snow_data[-1].depth_change
		print depth_change
		hello = "Station: %s, Snow depth: %s in., Depth change: %s in!" % (station.name, depth, depth_change)
		print hello
		message = client.messages.create(from_=TWILIO_NUMBER,
										to=number_to_text,
										body=hello)
		response = json.dumps(hello, message.sid)
		print message.sid
		return response
# End of Twilio test.

# ----------- 

# Alert functionality goes something like this:
# If user clicks set alert button, and user phone number is authenticated
# Add station, phone number to alert db and set alert status to false

# Every day cron job -- once running, put this into new file:
# Query station_ids found in the alerts table
	# alert_station = dbsession.query(model.Alerts).all()
	# for counter in alert_station:
# if depth_change > 0
		# d = dbsession.query(model.Stations).filter_by(alert_station.station_id)
		# u = d.snow_data[-1]
# if depth_change > 0
# and alert status = False
		# if u.depth_change > 0 and alert_station.status = False:
# Send alert to phone number for user_ids for that station_id
			# message_string = "Snow alert! Station: %s, Snow depth: %s in., Depth change: %s in!" % (d.name, u.depth, u.depth_change)
			# message = client.message.create(from = TWILIO_NUMBER,
			# 								to=alert_station.phone_number
			# 								body=message_string)
# Change alert status to True
			# alert_station.status =True
# Update datetime in last_alert
			# alert_station.date = datetime(now)
			# session.commit()
# if user replies to alert text
# Set alert status to False
# demo code - something like this:
	# from_number = request.values.get('From')
	# alert_station.phone_number.get(status) = False
	# session.commit()



if __name__ == "__main__":
    app.run(debug = True)
