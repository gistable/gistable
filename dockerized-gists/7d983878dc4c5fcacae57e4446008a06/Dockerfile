FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "enum"]
RUN ["pip", "install", "ijson"]
CMD ["python", "snippet.py"]