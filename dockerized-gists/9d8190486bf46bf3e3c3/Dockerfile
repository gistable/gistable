FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "gspread"]
RUN ["pip", "install", "pandas"]
CMD ["python", "snippet.py"]