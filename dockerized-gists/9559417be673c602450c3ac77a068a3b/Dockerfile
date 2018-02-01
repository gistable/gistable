FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "xvfbwrapper"]
RUN ["pip", "install", "lxml"]
RUN ["pip", "install", "selenium"]
CMD ["python", "snippet.py"]