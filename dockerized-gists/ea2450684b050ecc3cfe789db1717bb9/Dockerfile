FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "boto3"]
RUN ["pip", "install", "click"]
CMD ["python", "snippet.py"]