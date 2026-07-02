# gRPC > REST

## Decision: Use gRPC instead of a REST API

- Reason: Market data is a continuous stream
- Reason: Streaming RPCs naturally fit this behavior
- Reason: Lower overhead compared to repeated HTTP polling

