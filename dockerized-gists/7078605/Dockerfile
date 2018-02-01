FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "regex"]
RUN ["pip", "install", "clint"]
RUN ["pip", "install", "sarge"]
RUN ["pip", "install", "pathlib"]
RUN ["pip", "install", "clint"]
CMD ["python", "snippet.py"]