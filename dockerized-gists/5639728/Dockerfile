FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "paver"]
RUN ["pip", "install", "setuptools"]
RUN ["pip", "install", "pip"]
CMD ["python", "snippet.py"]