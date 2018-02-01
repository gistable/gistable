FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "cmemcache"]
RUN ["pip", "install", "memcache"]
RUN ["pip", "install", "werkzeug"]
RUN ["pip", "install", "pylibmc"]
CMD ["python", "snippet.py"]