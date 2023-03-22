FROM python:3-alpine 

RUN pip install httplib2


COPY src /src 
COPY dist /dist

WORKDIR /src

CMD ["/src/fetch-events.py"]