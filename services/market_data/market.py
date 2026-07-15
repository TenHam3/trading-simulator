import grpc
import os
import sys
from concurrent import futures
import time
import random
import logging
logger = logging.getLogger(__name__)
sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated'))

import marketdata_pb2
import marketdata_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

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
            logger.debug(f"Generated price tick - {price_tick.symbol}: {price_tick.price}")
            yield price_tick
            time.sleep(3)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    marketdata_pb2_grpc.add_StreamPricesServicer_to_server(MarketDataService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    serve()