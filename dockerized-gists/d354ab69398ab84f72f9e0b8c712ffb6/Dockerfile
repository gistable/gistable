FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "flask_sqlalchemy"]
RUN ["pip", "install", "flask_security"]
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "flask_login"]
RUN ["pip", "install", "flask_principal"]
RUN ["pip", "install", "flask_wtf"]
RUN ["pip", "install", "wtforms"]
RUN ["pip", "install", "wtforms"]
CMD ["python", "snippet.py"]