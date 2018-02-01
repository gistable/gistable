FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "gdata"]
RUN ["pip", "install", "lxml"]
RUN ["pip", "install", "gdata"]
RUN ["pip", "install", "dataset"]
RUN ["pip", "install", "atom"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "gdata"]
CMD ["python", "snippet.py"]