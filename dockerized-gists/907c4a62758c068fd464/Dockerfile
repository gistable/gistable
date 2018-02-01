FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "oauth2"]
RUN ["pip", "install", "tlslite"]
CMD ["python", "snippet.py"]