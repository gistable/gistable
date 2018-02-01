FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "humanize"]
RUN ["pip", "install", "bencodepy"]
CMD ["python", "snippet.py"]