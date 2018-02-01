FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "pyVim"]
RUN ["pip", "install", "pyVmomi"]
CMD ["python", "snippet.py"]