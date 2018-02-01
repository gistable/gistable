FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "tqdm"]
RUN ["pip", "install", "requests"]
RUN ["pip", "install", "PyPDF2"]
CMD ["python", "snippet.py"]