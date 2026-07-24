import grpc.aio
import asyncio
import os
import sys
import random
import logging
logger = logging.getLogger(__name__)
MKT_PORT = os.environ.get('MKT_PORT', '50051')
# sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated')) Uncomment only for direct runs from commandline

import marketdata_pb2
import marketdata_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

class MarketDataService(marketdata_pb2_grpc.MarketDataServiceServicer):
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
    marketdata_pb2_grpc.add_MarketDataServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f'[::]:{MKT_PORT}')
    await server.start()
    logger.info(f"Market Data service started on port {MKT_PORT}")
    await asyncio.gather(servicer.AdjustPrice(), server.wait_for_termination())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(serve())