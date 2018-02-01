FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "hoover"]
RUN ["pip", "install", "celery"]
CMD ["python", "snippet.py"]