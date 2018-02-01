FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "clr"]
RUN ["pip", "install", "WebsocketClient"]
CMD ["python", "snippet.py"]