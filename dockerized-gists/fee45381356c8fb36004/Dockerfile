FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "distance"]
RUN ["pip", "install", "pattern"]
RUN ["pip", "install", "networkx"]
RUN ["pip", "install", "pattern"]
CMD ["python", "snippet.py"]