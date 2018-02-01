FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "PIL"]
RUN ["pip", "install", "rsa"]
CMD ["python", "snippet.py"]