import grpc
import os
import sys
import logging
logger = logging.getLogger(__name__)
sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated'))

import portfolio_pb2
import portfolio_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50053') as port_channel:
        port_stub = portfolio_pb2_grpc.PortfolioServiceStub(port_channel)
        client_res = input("Do you want portfolio? ")
        while client_res != "q":
            if client_res == "y":
                response = port_stub.GetPortfolio(portfolio_pb2.PortfolioRequest())
                logger.info(f"Received portfolio: {response}")
                client_res = input("Do you want portfolio? ")
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    run()