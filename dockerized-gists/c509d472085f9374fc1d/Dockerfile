FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "ijson"]
RUN ["pip", "install", "cffi"]
RUN ["pip", "install", "ijson"]
CMD ["python", "snippet.py"]