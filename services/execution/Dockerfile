FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY generated ./generated
COPY services/execution .

ENV MKT_PORT=50051
ENV EX_PORT=50052
EXPOSE 50052

CMD ["python", "execution.py"]