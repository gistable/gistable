FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "blinker"]
RUN ["pip", "install", "inotifyx"]
CMD ["python", "snippet.py"]