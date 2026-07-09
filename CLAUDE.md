# CLAUDE.md

## Project Overview

### Project Name

Mini Distributed Trading Simulator

### Goal

Build a containerized distributed system consisting of several Python microservices that communicate via gRPC and asynchronous streams to simulate an automated trading workflow.

This project is intended to demonstrate:

* gRPC client/server communication
* Protocol Buffers
* Async programming with asyncio
* Docker containerization
* Distributed systems design
* Event-driven architecture
* Quantitative trading concepts
* Microservice architecture

The project should prioritize learning and clarity over production-grade complexity. This means that when asked questions during development, no code snippets should be generated and instead only hints or documentation details should be provided to guide the developer during development. Clarification of syntax with code is allowed if the user asks how to write a certain code snippet (with toy/irrelevant examples to the project

e.g., user asks how to write a gRPC service 
Response: 
```
service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply) {}
}
```
), 

but code snippets that directly implement a component of the project is not allowed.  

---

## Final Architecture

```text
                    +----------------+
                    | Market Data    |
                    +--------+-------+
                             |
                             | StreamPrices()
                             |
                             v
                    +----------------+
                    | Strategy       |
                    +--------+-------+
                             |
                             | SubmitOrder()
                             |
                             v
                    +----------------+
                    | Execution      |
                    +--------+-------+
                             |
                             | Fill Events
                             |
                             v
                    +----------------+
                    | Portfolio      |
                    +----------------+
```

Each service should run in its own Docker container.

Communication should use gRPC.

---

# Repository Structure

```text
trading-simulator/

├── requirements.txt
├── README.md
├── .gitignore
│
├── proto/
│
├── generated/
│
├── services/
│   ├── market_data/
│   ├── strategy/
│   ├── execution/
│   └── portfolio/
│
├── docs/
│   ├── architecture.md
│   ├── protobuf.md
│   ├── service-flows.md
│   └── diagrams/
│
└── docker-compose.yml
```

---

# Development Philosophy

Follow these principles:

1. Build incrementally.
2. Every phase must leave the system in a working state.
3. Do not introduce unnecessary technologies.
4. Prefer simplicity over cleverness.
5. Prioritize understanding over speed.
6. Add observability and testing early.
7. Avoid Kubernetes, Kafka, Redis, PostgreSQL, or other advanced infrastructure until the MVP is complete.

---

# Technology Stack

## Initial MVP

* Python 3.13
* grpcio
* grpcio-tools
* protobuf
* asyncio
* Docker
* Docker Compose

## Future Enhancements

* Redis
* PostgreSQL
* Prometheus
* Grafana
* Kafka or NATS
* Kubernetes

These are stretch goals only.

---

# Development Roadmap

---

## Phase 0 — Project Setup

### Objective

Create the repository structure and verify protobuf code generation.

### Tasks

* Create repository structure.
* Create Conda environment.
* Install dependencies.
* Create requirements.txt.
* Create .gitignore.
* Create proto directory.
* Create generated directory.
* Verify protobuf compilation.
* Build a Hello World gRPC server.
* Build a Hello World gRPC client.

### Deliverable

Understanding of:

```text
.proto
    ↓
generated code
    ↓
server
    ↓
client
```

---

## Phase 1 — Market Data Service

### Objective

Create a standalone microservice that simulates market data.

### Responsibilities

Generate fake price ticks.

Example:

```text
AAPL 100.00
AAPL 100.12
AAPL 99.97
```

### Protobuf Messages

PriceTick

Fields:

* symbol
* price
* timestamp

### RPC

```text
StreamPrices()
```

### Tasks

* Define protobuf schema.
* Generate protobuf stubs.
* Implement streaming gRPC server.
* Generate fake prices.
* Create test subscriber client.
* Verify live streaming works.

### Deliverable

Standalone market data service streaming prices continuously.

---

## Phase 2 — Strategy Service

### Objective

Consume market data and generate trading signals.

### Responsibilities

Receive price ticks and determine:

```text
BUY
SELL
HOLD
```

### Tasks

* Subscribe to StreamPrices().
* Maintain rolling price window.
* Calculate moving average.
* Generate BUY/SELL signals.
* Create Order objects.

### Example Logic

```python
if current_price > moving_average:
    BUY

if current_price < moving_average:
    SELL
```

### Deliverable

Strategy service generates signals from incoming market data.

---

## Phase 3 — Execution Service

### Objective

Act as a simplified exchange.

### Responsibilities

Receive orders and return fills.

### Protobuf Messages

Order

Fields:

* symbol
* side
* quantity

Fill

Fields:

* symbol
* price
* quantity

### RPC

```text
SubmitOrder()
```

### Tasks

* Create protobuf schema.
* Implement gRPC service.
* Accept incoming orders.
* Simulate fills.
* Return fill confirmations.

### Deliverable

Execution service capable of processing orders.

---

## Phase 4 — Connect Strategy and Execution

### Objective

Create the first complete workflow.

### Flow

```text
Market Tick
    ↓
Strategy
    ↓
Order
    ↓
Execution
```

### Tasks

* Connect Strategy to Market Data.
* Connect Strategy to Execution.
* Generate automatic orders.
* Log system events.
* Verify end-to-end operation.

### Deliverable

Working distributed trading workflow.

---

## Phase 5 — Portfolio Service

### Objective

Track positions and PnL.

### Responsibilities

Maintain:

* Position size
* Average cost
* Unrealized PnL

### Tasks

* Receive fills.
* Update positions.
* Track average cost.
* Calculate unrealized PnL.
* Expose portfolio state.

### Deliverable

Automated portfolio tracking.

---

## Phase 6 — Dockerization

### Objective

Containerize all services.

### Tasks

* Create Dockerfile for each service.
* Configure networking.
* Configure ports.
* Build docker-compose.yml.
* Verify services communicate in containers.

### Deliverable

Entire system starts with:

```bash
docker compose up
```

---

## Phase 7 — Async Improvements

### Objective

Introduce realistic distributed-system behavior.

### Tasks

* Use grpc.aio.
* Implement reconnect logic.
* Add retries.
* Add service heartbeats.
* Handle failures gracefully.

### Deliverable

Resilient asynchronous system.

---

## Phase 8 — Observability

### Objective

Make system behavior measurable.

### Tasks

* Structured logging.
* Request latency measurement.
* Throughput metrics.
* Error metrics.
* Service-level logging.

### Metrics

Track:

* ticks/sec
* orders/sec
* fills/sec
* average latency

### Deliverable

System health visibility.

---

# Service Responsibilities

## Market Data Service

Responsibilities:

* Generate price ticks.
* Stream ticks via gRPC.
* Simulate exchange feed.

Owns:

* Price generation logic.

---

## Strategy Service

Responsibilities:

* Consume market data.
* Generate signals.
* Submit orders.

Owns:

* Trading logic.

---

## Execution Service

Responsibilities:

* Accept orders.
* Simulate fills.
* Return execution reports.

Owns:

* Order processing.

---

## Portfolio Service

Responsibilities:

* Maintain positions.
* Track average cost.
* Compute PnL.

Owns:

* Portfolio state.

---

# MVP Definition

The MVP is complete when:

* Market Data streams prices.
* Strategy consumes prices.
* Strategy generates orders.
* Execution fills orders.
* Portfolio tracks positions.
* All services run via Docker Compose.
* Communication uses gRPC.
* The workflow runs automatically end-to-end.

---

# Stretch Goals

Only begin after MVP completion.

Potential enhancements:

1. Multiple symbols
2. Historical replay engine
3. Order book simulation
4. Redis cache
5. PostgreSQL persistence
6. Prometheus metrics
7. Grafana dashboards
8. Kafka or NATS
9. Monte Carlo pricing service
10. Kubernetes deployment

---

# Success Criteria

A successful project demonstrates:

* Understanding of gRPC
* Understanding of Protocol Buffers
* Understanding of asyncio
* Understanding of microservices
* Understanding of Docker
* Understanding of distributed communication
* Ability to explain system architecture clearly

The goal is educational value and demonstrable engineering skill, not production-grade trading infrastructure.
