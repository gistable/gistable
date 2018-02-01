FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "cuisine"]
RUN ["pip", "install", "fabtools"]
RUN ["pip", "install", "fabric"]
CMD ["python", "snippet.py"]