FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "packaging"]
RUN ["pip", "install", "cfscrape"]
CMD ["python", "snippet.py"]