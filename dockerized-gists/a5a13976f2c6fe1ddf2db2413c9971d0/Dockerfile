FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "datadog"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "urllib3"]
CMD ["python", "snippet.py"]