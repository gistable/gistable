FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "xml"]
RUN ["pip", "install", "termcolor"]
CMD ["python", "snippet.py"]