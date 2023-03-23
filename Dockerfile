FROM python:3-alpine 

RUN pip install \
    arrow \
    requests

COPY src /src 
COPY dist /dist

WORKDIR /src

CMD ["/src/fetch-events.py"]