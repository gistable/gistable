FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "docker"]
RUN ["pip", "install", "fabric"]
CMD ["python", "snippet.py"]