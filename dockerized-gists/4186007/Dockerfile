FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "xml"]
RUN ["pip", "install", "markdown"]
CMD ["python", "snippet.py"]