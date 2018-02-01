FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bs4"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "PIL"]
RUN ["pip", "install", "pytesseract"]
CMD ["python", "snippet.py"]