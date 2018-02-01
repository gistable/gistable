from celery.schedules import crontab
from flask.ext.celery import Celery

CELERYBEAT_SCHEDULE = {
	# executes every night at 4:15
	'every-night': {
		'task': 'user.checkaccounts',
		'schedule': crontab(hour=4, minute=20)
	}
}

celery = Celery(www)

@celery.task(name='user.checkaccounts')
def checkaccounts():
	# do something
	pass