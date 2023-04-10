FROM python:3-alpine 

RUN pip install \
    arrow \
    requests

COPY src /src 
COPY public /public

CMD ["python", "/src/fetch-events.py"]