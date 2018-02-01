FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bs4"]
RUN ["pip", "install", "dateutil"]
RUN ["pip", "install", "icalendar"]
CMD ["python", "snippet.py"]