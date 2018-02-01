from celery_app import Celery

celery = Celery("tasks", backend="amqp", broker="amqp://guest@localhost")

@celery.task(name='test_task')
def test_task():
	return "boom!"