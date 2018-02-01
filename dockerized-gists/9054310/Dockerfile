FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "rethinkdb"]
RUN ["pip", "install", "flask_security"]
RUN ["pip", "install", "flask_security"]
CMD ["python", "snippet.py"]