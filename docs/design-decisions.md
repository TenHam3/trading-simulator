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