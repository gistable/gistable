FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "unimportable_module"]
RUN ["pip", "install", "mock"]
CMD ["python", "snippet.py"]