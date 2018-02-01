FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "console"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "keychain"]
RUN ["pip", "install", "prettytable"]
CMD ["python", "snippet.py"]