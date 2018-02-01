FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "logging"]
RUN ["pip", "install", "gdata"]
CMD ["python", "snippet.py"]