FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "scapy"]
RUN ["pip", "install", "pefile"]
RUN ["pip", "install", "scapy_http"]
CMD ["python", "snippet.py"]