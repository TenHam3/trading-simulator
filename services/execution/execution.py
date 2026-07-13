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
    
    async def Submit(self, request, context):
        return execution_pb2.Fill(symbol=request.symbol, 
                                  price=self.prices.get(request.symbol), 
                                  quantity=request.quantity)
    
    async def get_market_data(self):
        async with grpc.aio.insecure_channel('localhost:50051') as mkt_channel:
            mkt_stub = marketdata_pb2_grpc.StreamPricesStub(mkt_channel)
            async for response in mkt_stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
                self.prices[response.symbol] = response.price
    
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