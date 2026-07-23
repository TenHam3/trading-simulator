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

class ExecutionService(execution_pb2_grpc.FillServiceServicer):
    def __init__(self):
        self.prices = {}
        self.events = {}
        self.fill_queues = set()
    
    async def GetFill(self, request, context):
        logger.info(f"Received order submission - {request.side} {request.quantity} {request.symbol}")
        if self.events.get(request.symbol) is None: self.events[request.symbol] = asyncio.Event()
        try:
            await asyncio.wait_for(self.events[request.symbol].wait(), timeout=3)
            logger.info(f"Filled order - {request.side} {request.quantity} {request.symbol} at price {self.prices.get(request.symbol)}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for market data for {request.symbol}")
            await context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, 
                                f"Timeout waiting for market data for symbol {request.symbol}")
        fill = execution_pb2.Fill(symbol=request.symbol, 
                                  price=self.prices.get(request.symbol), 
                                  side=request.side,
                                  quantity=request.quantity)
        for queue in self.fill_queues:
            await queue.put(fill)
        return fill
    
    async def StreamOrderFills(self, request, context):
        queue = asyncio.Queue()
        self.fill_queues.add(queue)
        try:
            while True:
                fill = await queue.get()
                yield fill
        finally:
            self.fill_queues.discard(queue)
    
    async def get_market_data(self):
        async with grpc.aio.insecure_channel('localhost:50051') as mkt_channel:
            mkt_stub = marketdata_pb2_grpc.MarketDataServiceStub(mkt_channel)
            async for response in mkt_stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
                self.prices[response.symbol] = response.price
                logger.debug(f"Updated price for {response.symbol}: {response.price}")
                if self.events.get(response.symbol) is None: self.events[response.symbol] = asyncio.Event()
                self.events[response.symbol].set()
    
async def serve():
    server = grpc.aio.server()
    servicer = ExecutionService()
    execution_pb2_grpc.add_FillServiceServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50052')
    await server.start()
    logger.info("Execution service started on port 50052")
    await asyncio.gather(servicer.get_market_data(), server.wait_for_termination())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(serve())