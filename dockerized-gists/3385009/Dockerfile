FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "myapp"]
RUN ["pip", "install", "mock"]
CMD ["python", "snippet.py"]