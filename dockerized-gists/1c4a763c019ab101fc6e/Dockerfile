FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "BeautifulSoup"]
RUN ["pip", "install", "reppy"]
CMD ["python", "snippet.py"]