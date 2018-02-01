FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pathlib"]
RUN ["pip", "install", "PyPDF2"]
CMD ["python", "snippet.py"]