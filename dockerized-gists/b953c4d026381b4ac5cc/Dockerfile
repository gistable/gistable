FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "pycurl2"]
RUN ["pip", "install", "pycurl"]
RUN ["pip", "install", "human_curl"]
CMD ["python", "snippet.py"]