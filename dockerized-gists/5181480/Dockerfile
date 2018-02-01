FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "webob"]
RUN ["pip", "install", "wsgiref"]
CMD ["python", "snippet.py"]