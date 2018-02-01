FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "delorean"]
RUN ["pip", "install", "alfred"]
CMD ["python", "snippet.py"]