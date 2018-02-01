FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "retryz"]
RUN ["pip", "install", "backoff"]
CMD ["python", "snippet.py"]