FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "django"]
RUN ["pip", "install", "wagtail"]
CMD ["python", "snippet.py"]