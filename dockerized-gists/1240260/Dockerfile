FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bson"]
RUN ["pip", "install", "pymongo"]
RUN ["pip", "install", "bson"]
CMD ["python", "snippet.py"]