FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "tqdm"]
RUN ["pip", "install", "multiprocessing"]
RUN ["pip", "install", "urllib3"]
CMD ["python", "snippet.py"]