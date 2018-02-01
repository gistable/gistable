FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "django"]
RUN ["pip", "install", "dateutil"]
RUN ["pip", "install", "app"]
RUN ["pip", "install", "redis"]
CMD ["python", "snippet.py"]