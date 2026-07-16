import grpc.aio
import asyncio
import os
import sys
import logging
logger = logging.getLogger(__name__)
sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated'))

import marketdata_pb2
import marketdata_pb2_grpc
import execution_pb2
import execution_pb2_grpc

async def get_market_data(self):
    async with grpc.aio.insecure_channel('localhost:50051') as mkt_channel:
        mkt_stub = marketdata_pb2_grpc.StreamPricesStub(mkt_channel)
        async for response in mkt_stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
            self.prices[response.symbol] = response.price
            logger.debug(f"Updated price for {response.symbol}: {response.price}")
            if self.events.get(response.symbol) is None: self.events[response.symbol] = asyncio.Event()
            self.events[response.symbol].set()

async def get_fills():
    async with grpc.aio.insecure_channel('localhost:50052') as ex_channel:
        ex_stub = execution_pb2_grpc.FillServiceStub(ex_channel)
        async for fill in ex_stub.StreamOrderFills(execution_pb2.SubscribeRequest()):
            logger.info(f"Received fill - {fill.side} {fill.quantity} {fill.symbol} at {fill.price}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(get_fills())
    