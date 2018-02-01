FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "PIL"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "pyquery"]
RUN ["pip", "install", "pytesseract"]
RUN ["pip", "install", "progressbar"]
CMD ["python", "snippet.py"]