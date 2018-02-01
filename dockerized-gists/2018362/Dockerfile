FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "celery"]
RUN ["pip", "install", "statsd"]
CMD ["python", "snippet.py"]