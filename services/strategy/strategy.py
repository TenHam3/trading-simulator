import grpc.aio
import asyncio
import os
import sys
import logging
logger = logging.getLogger(__name__)
MKT_PORT = os.environ.get('MKT_PORT', '50051')
EX_PORT = os.environ.get('EX_PORT', '50052')
MKT_HOST = os.environ.get('MKT_HOST', 'localhost')
EX_HOST = os.environ.get('EX_HOST', 'localhost')
# sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated')) Uncomment only for direct runs from commandline

import marketdata_pb2
import marketdata_pb2_grpc
import execution_pb2
import execution_pb2_grpc

TRADE_QTY = 1

async def run():
    async with grpc.aio.insecure_channel(f'{MKT_HOST}:{MKT_PORT}') as mkt_channel, grpc.aio.insecure_channel(f'{EX_HOST}:{EX_PORT}') as ex_channel:
        mkt_stub = marketdata_pb2_grpc.MarketDataServiceStub(mkt_channel)
        logger.info(f"Connected to Market Data Service on port {MKT_PORT}")
        ex_stub = execution_pb2_grpc.FillServiceStub(ex_channel)
        logger.info(f"Connected to Execution Service on port {EX_PORT}")
        price_window, held = [], 0
        async for response in mkt_stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
            symbol, price = response.symbol, response.price
            mvng_avg = sum(price_window) / len(price_window) if price_window else None
            logger.debug(f"Received price tick - {symbol}: {price}; Moving Average: {mvng_avg if mvng_avg else 'N/A'}")

            if len(price_window) >= 5:
                price_window.pop(0)
            price_window.append(price)

            if mvng_avg is None or ((abs(price - mvng_avg) / mvng_avg) < 0.005):
                logger.info(f"HOLD {TRADE_QTY} {symbol} at {price} (AVG: {mvng_avg if mvng_avg else 'N/A'})")
            else:
                order = execution_pb2.Order()
                if price > mvng_avg:
                    order.symbol = response.symbol
                    order.side = 'BUY'
                    order.quantity = TRADE_QTY
                    logger.info(f"BUY {TRADE_QTY} {symbol} at {price} (AVG: {mvng_avg})")

                    try:
                        fill = await ex_stub.GetFill(order)
                        held += TRADE_QTY
                        logger.info(f"Filled BUY {TRADE_QTY} {symbol} at {fill.price}")
                    except grpc.RpcError as e:
                        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                            logger.error(f"Order submission for {symbol} timed out: {e.details()}")
                        else:
                            raise
                elif held > 0:
                    order.symbol = response.symbol
                    order.side = 'SELL'
                    order.quantity = TRADE_QTY
                    logger.info(f"SELL {TRADE_QTY} {symbol} at {price} (AVG: {mvng_avg})")

                    try:
                        fill = await ex_stub.GetFill(order)
                        logger.info(f"Filled SELL {TRADE_QTY} {symbol} at {fill.price}")
                        held -= TRADE_QTY
                    except grpc.RpcError as e:
                        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                            logger.error(f"Order submission for {symbol} timed out: {e.details()}")
                        else:
                            raise
                else:
                    logger.info(f"HOLD {TRADE_QTY} {symbol} at {price} (AVG: {mvng_avg})")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(run())