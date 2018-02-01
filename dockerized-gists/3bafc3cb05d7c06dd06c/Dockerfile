FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "certifi"]
RUN ["pip", "install", "elasticsearch"]
RUN ["pip", "install", "elasticsearch"]
RUN ["pip", "install", "requests_aws4auth"]
CMD ["python", "snippet.py"]