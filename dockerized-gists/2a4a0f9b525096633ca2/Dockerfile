FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "flask_login"]
RUN ["pip", "install", "flask_googlelogin"]
CMD ["python", "snippet.py"]