FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "email"]
RUN ["pip", "install", "xlrd"]
RUN ["pip", "install", "email"]
RUN ["pip", "install", "xlwt"]
CMD ["python", "snippet.py"]