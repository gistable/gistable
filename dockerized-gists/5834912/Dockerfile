FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "mimerender"]
RUN ["pip", "install", "xhtml2pdf"]
CMD ["python", "snippet.py"]