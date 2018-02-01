FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "xmlrpc"]
CMD ["python", "snippet.py"]