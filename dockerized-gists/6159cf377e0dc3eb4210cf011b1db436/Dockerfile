FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "parse"]
RUN ["pip", "install", "serial"]
CMD ["python", "snippet.py"]