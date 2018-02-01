FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "psutil"]
RUN ["pip", "install", "setproctitle"]
CMD ["python", "snippet.py"]