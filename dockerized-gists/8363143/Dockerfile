FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "simple_salesforce"]
CMD ["python", "snippet.py"]