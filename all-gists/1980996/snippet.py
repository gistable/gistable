from celery.task.control import task, rate_limit


def send_shit(article):
    ...


def user_send(user, article):
    taskname = "send.{user}".format(user.name)

    t = task(name=taskname)(send_shit)
    rate_limit(taskname, "1/s")

    return t(article)