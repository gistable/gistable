FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "selenium"]
RUN ["pip", "install", "BeautifulSoup"]
RUN ["pip", "install", "openpyxl"]
RUN ["pip", "install", "pandas"]
CMD ["python", "snippet.py"]