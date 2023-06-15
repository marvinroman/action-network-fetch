FROM python:3.11.4-alpine

COPY src /src 

RUN pip install -r /src/requirements.txt

COPY public /public

CMD ["python", "/src/fetch-events.py"]