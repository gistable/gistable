FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "sqlalchemy"]
RUN ["pip", "install", "quick_orm"]
RUN ["pip", "install", "bottlenose"]
RUN ["pip", "install", "BeautifulSoup"]
RUN ["pip", "install", "socks"]
RUN ["pip", "install", "xlrd"]
RUN ["pip", "install", "TorCtl"]
CMD ["python", "snippet.py"]