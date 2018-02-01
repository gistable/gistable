FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "flask_restful"]
RUN ["pip", "install", "flask_pymongo"]
CMD ["python", "snippet.py"]