FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "semantics3"]
RUN ["pip", "install", "eventlet"]
CMD ["python", "snippet.py"]