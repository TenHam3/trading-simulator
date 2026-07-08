import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated'))

import marketdata_pb2
import marketdata_pb2_grpc
import grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = marketdata_pb2_grpc.StreamPricesStub(channel)
        for response in stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
            print(f"MarketData client received: {response}")

if __name__ == '__main__':
    run()