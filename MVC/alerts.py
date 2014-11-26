import model
from model import Alert
from datetime import datetime
from sqlalchemy import Table, Column, Float, Integer, Boolean, String, MetaData, ForeignKey

def load_alert(from_number, station):
	alert = None
	station_id = model.session.query(model.Station).filter_by(id=station).one()
	alert = model.Alert(\
		phone_number = from_number,\
		station_id = station_id.id,\
		status = 1)
	print alert
	model.session.add(alert)
	model.session.commit()
