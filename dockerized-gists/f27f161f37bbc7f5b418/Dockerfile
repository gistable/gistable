FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pytz"]
RUN ["pip", "install", "pinboard"]
CMD ["python", "snippet.py"]