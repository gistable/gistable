FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "pymongo"]
RUN ["pip", "install", "werkzeug"]
CMD ["python", "snippet.py"]