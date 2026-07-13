import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../generated'))

import marketdata_pb2
import marketdata_pb2_grpc
import execution_pb2
import execution_pb2_grpc
import grpc

TRADE_QTY = 1

def run():
    with grpc.insecure_channel('localhost:50051') as mkt_channel, grpc.insecure_channel('localhost:50052') as ex_channel:
        mkt_stub = marketdata_pb2_grpc.StreamPricesStub(mkt_channel)
        ex_stub = execution_pb2_grpc.SubmitOrderStub(ex_channel)
        price_window, held = [], 0
        for response in mkt_stub.StreamPriceTicks(marketdata_pb2.SubscribeRequest()):
            price = response.price
            mvng_avg = sum(price_window) / len(price_window) if price_window else None

            if len(price_window) >= 5:
                price_window.pop(0)
            price_window.append(price)

            if mvng_avg is None or ((abs(price - mvng_avg) / mvng_avg) < 0.005):
                print(f"HOLD: {response.symbol} at {price};\nTime: {response.timestamp}Ratio: {(abs(price - mvng_avg) / mvng_avg) if mvng_avg else 'N/A'}\n")
            else:
                order = execution_pb2.Order()
                if price > mvng_avg:
                    held += TRADE_QTY
                    order.symbol = response.symbol
                    order.side = 'BUY'
                    order.quantity = TRADE_QTY
                    fill = ex_stub.Submit(order)
                    print(f"BUY: {response.symbol} at {price};\nTime: {response.timestamp}Ratio: {(abs(price - mvng_avg) / mvng_avg)}\n")
                    print(f"Fill: {fill}\n")
                elif held > 0:
                    held -= TRADE_QTY
                    order.symbol = response.symbol
                    order.side = 'SELL'
                    order.quantity = TRADE_QTY
                    fill = ex_stub.Submit(order)
                    print(f"SELL: {response.symbol} at {price};\nTime: {response.timestamp}Ratio: {(abs(price - mvng_avg) / mvng_avg)}\n")
                    print(f"Fill: {fill}\n")
                else:
                    print(f"HOLD: {response.symbol} at {price};\nTime: {response.timestamp}Ratio: {(abs(price - mvng_avg) / mvng_avg)}\n")
                if order: print(f"Order: {order}\n")

if __name__ == '__main__':
    run()