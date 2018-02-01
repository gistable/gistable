FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "tqdm"]
RUN ["pip", "install", "elasticsearch"]
RUN ["pip", "install", "pymongo"]
RUN ["pip", "install", "elasticsearch"]
CMD ["python", "snippet.py"]