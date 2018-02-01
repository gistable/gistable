FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "lxml"]
RUN ["pip", "install", "os"]
CMD ["python", "snippet.py"]