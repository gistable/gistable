FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "imdbpie"]
RUN ["pip", "install", "plexapi"]
RUN ["pip", "install", "rotten_tomatoes_client"]
CMD ["python", "snippet.py"]