FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "unidecode"]
RUN ["pip", "install", "bucket3"]
RUN ["pip", "install", "docopt"]
CMD ["python", "snippet.py"]