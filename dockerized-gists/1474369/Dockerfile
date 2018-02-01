FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "django"]
RUN ["pip", "install", "lxml"]
RUN ["pip", "install", "BeautifulSoup"]
RUN ["pip", "install", "cannonball"]
CMD ["python", "snippet.py"]