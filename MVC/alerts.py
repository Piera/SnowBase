import os
import model
from model import Alert
from datetime import datetime
from twilio.rest import TwilioRestClient
from sqlalchemy import update
from sqlalchemy import Table, Column, Float, Integer, Boolean, String, MetaData, ForeignKey

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

def load_alert(from_number, station):
	alert = None
	# station_id = model.session.query(model.Station).filter_by(id=station).one()
	# print station_id.id
	alert = model.Alert(\
		phone_number = from_number,\
		station_id = station,\
		status = True
		)
	model.session.add(alert)
	model.session.commit()

def update_alert(alert_id, alert_status):
	alert = model.session.query(model.Alert).filter_by(id=alert_id)
	alert[0].status=False
	model.session.commit()