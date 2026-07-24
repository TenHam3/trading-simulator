FROM python:3.13-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY generated ./generated
COPY services/market_data .

ENV MARKET_PORT=50051
EXPOSE 50051

CMD ["python", "market.py"]