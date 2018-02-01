FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "lxml"]
RUN ["pip", "install", "human_curl"]
CMD ["python", "snippet.py"]