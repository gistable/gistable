FROM python:2.7.13
ADD snippet.py snippet.py
RUN ["pip", "install", "urllib"]
RUN ["pip", "install", "jwt"]
RUN ["pip", "install", "cherrypy"]
RUN ["pip", "install", "urllib"]
CMD ["python", "snippet.py"]