FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "nitrate"]
RUN ["pip", "install", "kerberos"]
CMD ["python", "snippet.py"]