FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "simplejson"]
RUN ["pip", "install", "networkx"]
CMD ["python", "snippet.py"]