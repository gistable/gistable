FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "requests_toolbelt"]
RUN ["pip", "install", "gevent"]
CMD ["python", "snippet.py"]