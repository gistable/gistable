FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "dateutil"]
RUN ["pip", "install", "psycopg2"]
RUN ["pip", "install", "cx_Oracle"]
RUN ["pip", "install", "MySQLdb"]
RUN ["pip", "install", "pandas"]
RUN ["pip", "install", "numpy"]
RUN ["pip", "install", "pandas"]
CMD ["python", "snippet.py"]