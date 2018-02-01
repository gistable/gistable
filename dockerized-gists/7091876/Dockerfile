FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bs4"]
RUN ["pip", "install", "mysolr"]
RUN ["pip", "install", "pandas"]
RUN ["pip", "install", "luigi"]
CMD ["python", "snippet.py"]