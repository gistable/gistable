FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pyrax"]
RUN ["pip", "install", "novaclient"]
CMD ["python", "snippet.py"]