FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "unittest2"]
RUN ["pip", "install", "logging_subprocess"]
CMD ["python", "snippet.py"]