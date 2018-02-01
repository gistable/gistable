FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "requests_cache"]
RUN ["pip", "install", "click"]
CMD ["python", "snippet.py"]