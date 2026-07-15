import grpc.aio
import asyncio
import os
import sys
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

    async def AdjustPrice(self):
        while True:
            self.price *= (1 + random.gauss(0, 0.005))
            await asyncio.sleep(1)


    async def StreamPriceTicks(self, request, context):
        while True:
            symbol = "AAPL"
            ts = Timestamp()
            ts.GetCurrentTime()
            price_tick = marketdata_pb2.PriceTick(symbol=symbol, 
                                        price=self.price, 
                                        timestamp=ts)
            logger.debug(f"Generated price tick - {price_tick.symbol}: {price_tick.price}")
            yield price_tick
            await asyncio.sleep(3)

async def serve():
    server = grpc.aio.server()
    servicer = MarketDataService()
    marketdata_pb2_grpc.add_StreamPricesServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    logger.info("Market Data service started on port 50051")
    await asyncio.gather(servicer.AdjustPrice(), server.wait_for_termination())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(serve())