FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bs4"]
RUN ["pip", "install", "pySmartDL"]
RUN ["pip", "install", "os"]
RUN ["pip", "install", "cfscrape"]
CMD ["python", "snippet.py"]