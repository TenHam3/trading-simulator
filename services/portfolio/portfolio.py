import grpc.aio
import asyncio
import os
import sys
import logging
from google.protobuf.timestamp_pb2 import Timestamp
logger = logging.getLogger(__name__)
sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated'))

import marketdata_pb2
import marketdata_pb2_grpc
import execution_pb2
import execution_pb2_grpc
import portfolio_pb2
import portfolio_pb2_grpc

class PortfolioService(portfolio_pb2_grpc.PortfolioServiceServicer):
    def __init__(self):
        self.prices = {}
        self.events = {}
        self.portfolio = portfolio_pb2.Portfolio()

    async def GetPortfolio(self, request, context):
        logger.debug(f"Returned portfolio: {self.portfolio}")
        return self.portfolio

    async def get_market_data(self):
        async with grpc.aio.insecure_channel('localhost:50051') as mkt_channel:
            mkt_stub = marketdata_pb2_grpc.StreamPricesStub(mkt_channel)
            logger.info("Connected to Market Data Service on port 50051")
            async for response in mkt_stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
                self.prices[response.symbol] = response.price
                logger.debug(f"Updated price for {response.symbol}: {response.price}")
                if self.events.get(response.symbol) is None: self.events[response.symbol] = asyncio.Event()
                self.events[response.symbol].set()

    async def get_fills(self):
        async with grpc.aio.insecure_channel('localhost:50052') as ex_channel:
            ex_stub = execution_pb2_grpc.FillServiceStub(ex_channel)
            logger.info("Connected to Execution Service on port 50052")
            async for fill in ex_stub.StreamOrderFills(execution_pb2.SubscribeRequest()):
                logger.info(f"Received fill - {fill.side} {fill.quantity} {fill.symbol} at {fill.price}")
                if self.events.get(fill.symbol) is None: self.events[fill.symbol] = asyncio.Event()
                try:
                    await asyncio.wait_for(self.events[fill.symbol].wait(), timeout=3)
                    curr_price = self.prices.get(fill.symbol)
                except asyncio.TimeoutError:
                    logger.error(f"Timeout waiting for market data for {fill.symbol}")
                    continue
                ts = Timestamp()
                ts.GetCurrentTime()
                if fill.symbol not in self.portfolio.positions:
                    if fill.side == "SELL": 
                        logger.warning(f"Rejected fill - Attempted to oversell {fill.quantity} {fill.symbol} with no current holdings")
                        continue
                    logger.info(f"Opened new position - {fill.quantity} {fill.symbol} at {fill.price}")
                    self.portfolio.positions[fill.symbol].CopyFrom(portfolio_pb2.Position(size=fill.quantity,
                                                                         average_cost=fill.price,
                                                                         current_price=curr_price,
                                                                         unrealized_pnl=(curr_price - fill.price) * fill.quantity,
                                                                         realized_pnl=0.0,
                                                                         timestamp=ts))
                else:
                    position = self.portfolio.positions[fill.symbol]
                    if fill.side =="BUY":
                        avg_cost = (position.size * position.average_cost + fill.quantity * fill.price) / (position.size + fill.quantity)
                        valid_sell = False
                        position.size += fill.quantity
                    else:
                        avg_cost = position.average_cost
                        valid_sell = fill.quantity <= position.size
                        if valid_sell:
                            position.size -= fill.quantity    
                            position.realized_pnl += (fill.price - position.average_cost) * fill.quantity
                        else:
                            logger.warning(f"Rejected fill - Attempted to oversell {fill.quantity} {fill.symbol} when size is only {position.size}")
                            continue

                    position.average_cost = avg_cost
                    position.current_price = curr_price
                    position.unrealized_pnl = (curr_price - avg_cost) * position.size
                    position.timestamp.CopyFrom(ts)
                    logger.info(f"Updated position for {fill.symbol} - Size: {position.size}; Avg. Cost: {avg_cost}; UPnL: {position.unrealized_pnl}{f"; RPnL: {position.realized_pnl}" if fill.side == "SELL" else ""}")

async def serve():
    server = grpc.aio.server()
    servicer = PortfolioService()
    portfolio_pb2_grpc.add_PortfolioServiceServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50053')
    await server.start()
    logger.info("Portfolio service started on port 50053")
    await asyncio.gather(servicer.get_market_data(), servicer.get_fills(), server.wait_for_termination())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(serve())
    