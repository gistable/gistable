FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "petl"]
RUN ["pip", "install", "os"]
RUN ["pip", "install", "psycopg2"]
CMD ["python", "snippet.py"]