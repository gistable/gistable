FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "libgreader"]
RUN ["pip", "install", "couchdb"]
CMD ["python", "snippet.py"]