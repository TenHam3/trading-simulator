import grpc
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated'))

import marketdata_pb2
import marketdata_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

from concurrent import futures
import time
import random

class MarketDataService(marketdata_pb2_grpc.StreamPricesServicer):
    def __init__(self):
        self.price = 100.0

    def GeneratePriceTick(self):
        symbol = "AAPL"
        self.price *= (1 + random.gauss(0, 0.005))
        ts = Timestamp()
        ts.GetCurrentTime()
        return marketdata_pb2.PriceTick(symbol=symbol, 
                                        price=self.price, 
                                        timestamp=ts)


    def StreamPriceTicks(self, request, context):
        while True:
            price_tick = self.GeneratePriceTick()
            yield price_tick
            time.sleep(1)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    marketdata_pb2_grpc.add_StreamPricesServicer_to_server(MarketDataService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()