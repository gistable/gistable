FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "zmq"]
RUN ["pip", "install", "twisted"]
CMD ["python", "snippet.py"]