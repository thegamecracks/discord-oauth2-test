FROM python:3.11-alpine

WORKDIR app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY app/ app/

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "app:app"]
