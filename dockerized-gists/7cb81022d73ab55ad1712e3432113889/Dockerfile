FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "epubzilla"]
RUN ["pip", "install", "pygame"]
CMD ["python", "snippet.py"]