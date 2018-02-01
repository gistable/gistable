FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "whisper"]
RUN ["pip", "install", "cql"]
CMD ["python", "snippet.py"]