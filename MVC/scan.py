import os
import model
import operator
from alerts import update_alert
from twilio.rest import TwilioRestClient
from sqlalchemy import select

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# Scans for alerts, sends alerts, updates alerts
def alert_scan(session):
	station = None
	all_alerts = session.query(model.Alert).all()
	client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
	for alert in all_alerts:
		station = alert.station_id
		# report = session.query(model.Station).get(station).all()
		report = session.query(model.Station).get(station)

		# Check for depth data for station:
		try:
			depth = report.snow_data[-1].depth
			depth_change = report.snow_data[-1].depth_change
		except IndexError:
			depth_change = 0

		# If there is data, check if there is depth change and send alert:
		if depth_change > 0:
			if alert.status==True:
				update = "New snow alert! Station: %s, Snow depth: %s in., Depth change: %s in. To reset this alert, respond to this text with %s." % (report.name, depth, depth_change, station)
				message = client.messages.create(from_=TWILIO_NUMBER,
											to=alert.phone_number,
											body=update)
				update_alert(alert.id, alert.status)
		else:
			continue

def main(session):
	alert_scan(session)
    
if __name__ == "__main__":
    s = model.session
    main(s)
