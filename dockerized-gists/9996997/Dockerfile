FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "websocket"]
RUN ["pip", "install", "win32api"]
CMD ["python", "snippet.py"]