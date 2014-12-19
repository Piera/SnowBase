from apscheduler.schedulers.blocking import BlockingScheduler
from add import load_snow_data
import model
# from add import alert_scan
# import model

# sched = BlockingScheduler()
# @sched.scheduled_job('interval', minutes=5)
# sched.add_job(load_snow_data, 'interval', minutes=1)
def timed_job():
	load_snow_data()

# sched.add_job(timed_job, 'interval', minutes=1)
# @sched.scheduled_job('cron', day_of_week='mon-sun', hours=5)
# def scheduled_job():
#   load_snow_data(session)
# 	alert_scan(session)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(timed_job, 'interval', minutes=1)
    # print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    print 'OK, I am running'

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

# sched.start()