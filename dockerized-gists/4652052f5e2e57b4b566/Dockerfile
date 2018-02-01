FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "ansible"]
RUN ["pip", "install", "jinja2"]
CMD ["python", "snippet.py"]