FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pytumblr"]
RUN ["pip", "install", "oauth2"]
CMD ["python", "snippet.py"]