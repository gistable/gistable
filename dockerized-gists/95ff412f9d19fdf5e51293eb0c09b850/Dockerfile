FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "flask"]
RUN ["pip", "install", "flask_cors"]
RUN ["pip", "install", "pandas"]
CMD ["python", "snippet.py"]