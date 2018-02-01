FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "six"]
RUN ["pip", "install", "marshmallow"]
CMD ["python", "snippet.py"]