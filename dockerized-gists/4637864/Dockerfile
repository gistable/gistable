FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "requests_oauthlib"]
CMD ["python", "snippet.py"]