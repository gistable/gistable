FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "serial"]
RUN ["pip", "install", "proton"]
CMD ["python", "snippet.py"]