import grpc.aio
import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated'))

import marketdata_pb2
import marketdata_pb2_grpc
import execution_pb2
import execution_pb2_grpc

class ExecutionService(execution_pb2_grpc.SubmitOrderServicer):
    def __init__(self):
        self.prices = {}
        self.events = {}
    
    async def Submit(self, request, context):
        if self.events.get(request.symbol) is None: self.events[request.symbol] = asyncio.Event()
        try:
            await asyncio.wait_for(self.events[request.symbol].wait(), timeout=3)
        except asyncio.TimeoutError:
            await context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, 
                                f"Timeout waiting for market data for symbol {request.symbol}")
        return execution_pb2.Fill(symbol=request.symbol, 
                                  price=self.prices.get(request.symbol), 
                                  quantity=request.quantity)
    
    async def get_market_data(self):
        async with grpc.aio.insecure_channel('localhost:50051') as mkt_channel:
            mkt_stub = marketdata_pb2_grpc.StreamPricesStub(mkt_channel)
            async for response in mkt_stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
                self.prices[response.symbol] = response.price
                if self.events.get(response.symbol) is None: self.events[response.symbol] = asyncio.Event()
                self.events[response.symbol].set()
    
async def serve():
    server = grpc.aio.server()
    servicer = ExecutionService()
    execution_pb2_grpc.add_SubmitOrderServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50052')
    await server.start()
    print("Server started on port 50052")
    await asyncio.gather(servicer.get_market_data(), server.wait_for_termination())

if __name__ == '__main__':
    asyncio.run(serve())