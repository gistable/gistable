FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "NetEaseMusicApi"]
RUN ["pip", "install", "itchat"]
CMD ["python", "snippet.py"]