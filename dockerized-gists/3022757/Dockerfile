FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "docopt"]
RUN ["pip", "install", "envoy"]
CMD ["python", "snippet.py"]