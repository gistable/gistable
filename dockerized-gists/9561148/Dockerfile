FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "psycopg2"]
RUN ["pip", "install", "flask_peewee"]
CMD ["python", "snippet.py"]