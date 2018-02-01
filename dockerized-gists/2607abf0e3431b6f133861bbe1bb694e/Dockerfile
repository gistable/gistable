FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "xmltodict"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "plexapi"]
CMD ["python", "snippet.py"]