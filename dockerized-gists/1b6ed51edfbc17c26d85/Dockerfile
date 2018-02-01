FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pandas"]
RUN ["pip", "install", "psycopg2"]
RUN ["pip", "install", "sqlalchemy"]
RUN ["pip", "install", "pandas"]
RUN ["pip", "install", "boto"]
CMD ["python", "snippet.py"]