FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "werkzeug"]
RUN ["pip", "install", "simplejson"]
RUN ["pip", "install", "bson"]
CMD ["python", "snippet.py"]