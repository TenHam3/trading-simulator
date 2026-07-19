# gRPC > REST

## Decision: Use gRPC instead of a REST API

- Reason: Market data is a continuous stream
- Reason: Streaming RPCs naturally fit this behavior
- Reason: Lower overhead compared to repeated HTTP polling

# Market Data Random Walk Design

## Decision: Normal Distribution for Randomized Price Fluctuation

- Reason: Uniform distribution gives equal probability to large and small price fluctuations => unrealistic
- Reason: Simple and effective model to mimic random prices. Drift term may be needed if incoming prices do not have a strong signal for the Strategy engine's moving-average to act

## Decision: Maintain Price as an Instance-level Class Member

- Reason: Future multi-symbol support requires this since the same Market Data process can spawn multiple MarketDataService instances (for each symbol) with their own price variables

# Async Market Data and Execution

## Decision: Transitioned Market Data and Execution Services to Async

- Reason: Allows both services to run concurrent services asynchronously -> decouples different functions of each service (managing market data state vs streaming market data; consuming stream of market data vs fulfilling Fill responses to Strategy)
- Reason: Market Data now has a task that solely maintains market data prices while a separate task is responsible for reading from and streaming this state to clients; makes Market Data Service a consistent, source of truth for market data 
- Reason: Execution can now act as a dual-role service of both client (consuming market data stream) and server (serving Fill responses to Strategy Orders)

## Decision: Handled Price Races with Per-Symbol asyncio Events

- Reason: Avoids data races and errors related to Strategy requesting Fills before Execution Service has any existing market data on the requested symbol
- Reason: Gives Strategy a defined gRPC error instead of an unhandled exception