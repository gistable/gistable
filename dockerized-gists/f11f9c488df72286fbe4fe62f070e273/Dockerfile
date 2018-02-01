FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "urllib3"]
RUN ["pip", "install", "xml"]
CMD ["python", "snippet.py"]