FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "nbformat"]
RUN ["pip", "install", "lib2to3"]
RUN ["pip", "install", "pathlib"]
CMD ["python", "snippet.py"]