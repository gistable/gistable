FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "gevent"]
RUN ["pip", "install", "dnslib"]
CMD ["python", "snippet.py"]