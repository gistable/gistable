FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "daemon"]
RUN ["pip", "install", "lockfile"]
RUN ["pip", "install", "eventlet"]
CMD ["python", "snippet.py"]