FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "grapefruit"]
RUN ["pip", "install", "fabulous"]
CMD ["python", "snippet.py"]