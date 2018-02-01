FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "loggerglue"]
RUN ["pip", "install", "raven"]
CMD ["python", "snippet.py"]