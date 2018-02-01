FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "bitmerchant"]
RUN ["pip", "install", "mnemonic"]
CMD ["python", "snippet.py"]