FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "tnetstring"]
RUN ["pip", "install", "werkzeug"]
RUN ["pip", "install", "users"]
CMD ["python", "snippet.py"]