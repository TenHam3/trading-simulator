import grpc.aio
import asyncio
import os
import sys
import logging
from google.protobuf.timestamp_pb2 import Timestamp
logger = logging.getLogger(__name__)
MKT_PORT = os.environ.get('MKT_PORT', '50051')
EX_PORT = os.environ.get('EX_PORT', '50052')
PORTFOLIO_PORT = os.environ.get('PORTFOLIO_PORT', '50053')
MKT_HOST = os.environ.get('MKT_HOST', 'localhost')
EX_HOST = os.environ.get('EX_HOST', 'localhost')
# sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated')) Uncomment only for direct runs from commandline

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
        async with grpc.aio.insecure_channel(f'{MKT_HOST}:{MKT_PORT}') as mkt_channel:
            mkt_stub = marketdata_pb2_grpc.MarketDataServiceStub(mkt_channel)
            logger.info(f"Connected to Market Data Service on port {MKT_PORT}")
            async for response in mkt_stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
                symbol, curr_price = response.symbol, response.price
                self.prices[symbol] = curr_price
                logger.debug(f"Updated price for {response.symbol}: {response.price}")
                if symbol in self.portfolio.positions:
                    position = self.portfolio.positions[symbol]
                    ts = Timestamp()
                    ts.GetCurrentTime()
                    position.current_price = curr_price
                    position.timestamp.CopyFrom(ts)
                    position.unrealized_pnl = (curr_price - position.average_cost) * position.size
                    logger.debug(f"Updated UPnL for {symbol} - UPnL: {position.unrealized_pnl} with current price {curr_price}")
                if self.events.get(response.symbol) is None: self.events[response.symbol] = asyncio.Event()
                self.events[response.symbol].set()

    async def get_fills(self):
        async with grpc.aio.insecure_channel(f'{EX_HOST}:{EX_PORT}') as ex_channel:
            ex_stub = execution_pb2_grpc.FillServiceStub(ex_channel)
            logger.info(f"Connected to Execution Service on port {EX_PORT}")
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
    server.add_insecure_port(f'[::]:{PORTFOLIO_PORT}')
    await server.start()
    logger.info(f"Portfolio service started on port {PORTFOLIO_PORT}")
    await asyncio.gather(servicer.get_market_data(), servicer.get_fills(), server.wait_for_termination())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(serve())
    