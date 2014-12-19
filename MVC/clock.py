from apscheduler.schedulers.blocking import BlockingScheduler
from add.py import load_snow_data
from add.py import alert_scan

sched = BlockingScheduler()

# @sched.scheduled_job('interval', minutes=3)
# def timed_job(session):
# 	load_snow_data(session)
# 	alert_scan(session)
    

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=4)
def scheduled_job():
    load_snow_data(session)
	alert_scan(session)

sched.start()