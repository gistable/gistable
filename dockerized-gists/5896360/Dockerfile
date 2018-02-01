FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "daemon"]
RUN ["pip", "install", "libgreader"]
RUN ["pip", "install", "pony"]
CMD ["python", "snippet.py"]