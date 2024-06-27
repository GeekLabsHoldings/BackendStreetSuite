from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .scheduler import upgrade_to_monthly

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(upgrade_to_monthly, CronTrigger(hour=0, minute=0))
    scheduler.start()