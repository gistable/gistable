FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "BeautifulSoup"]
RUN ["pip", "install", "nltk"]
CMD ["python", "snippet.py"]