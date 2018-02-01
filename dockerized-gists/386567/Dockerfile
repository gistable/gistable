FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "local_fabfile"]
RUN ["pip", "install", "fabric"]
CMD ["python", "snippet.py"]