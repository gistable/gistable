FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "networkx"]
RUN ["pip", "install", "xml"]
CMD ["python", "snippet.py"]