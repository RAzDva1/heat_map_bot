from apscheduler.schedulers.background import BackgroundScheduler

from main import send_message_by_scheldier


def print_hel(arh):
    print("Hello, ", arh)

sched = BackgroundScheduler(deamon=True)
sched.add_job(print_hel, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=15)

sched.add_job(print_hel, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=30)

sched.add_job(print_hel, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=45)

sched.start()
