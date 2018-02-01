FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pynotify"]
RUN ["pip", "install", "pygame"]
CMD ["python", "snippet.py"]