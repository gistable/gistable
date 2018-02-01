FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "distutils"]
RUN ["pip", "install", "six"]
CMD ["python", "snippet.py"]