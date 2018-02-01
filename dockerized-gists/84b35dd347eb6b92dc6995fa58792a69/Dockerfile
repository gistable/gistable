FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bs4"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "more_itertools"]
RUN ["pip", "install", "pandas"]
CMD ["python", "snippet.py"]