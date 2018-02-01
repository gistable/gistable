FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "gevent"]
RUN ["pip", "install", "httplib2"]
CMD ["python", "snippet.py"]