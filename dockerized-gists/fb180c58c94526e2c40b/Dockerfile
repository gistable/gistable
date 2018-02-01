FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "console"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "ui"]
CMD ["python", "snippet.py"]