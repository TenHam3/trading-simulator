# Project Overview

This project is a containerized distributed trading simulator built to demonstrate modern backend and distributed systems concepts. The application is composed of multiple Python microservices that communicate using gRPC and Protocol Buffers, with asynchronous streaming used to simulate real-time market data.

The simulator models the lifecycle of an automated trading system, including market data generation, trading strategy evaluation, order execution, and portfolio management. While the trading logic is intentionally simple, the primary goal is to showcase microservice architecture, inter-service communication, and reproducible deployment using Docker.

# Tech Stack

- Python (3.13)
- gRPC
- Protocol Buffers
- asyncio
- Docker
- Docker Compose

# Repository Structure

trading-simulator/

├── proto/
├── generated/
├── services/
│   ├── market_data/
│   ├── strategy/
│   ├── execution/
│   └── portfolio/
├── docs/
├── docker-compose.yml
└── README.md

# How to Run

## Environment Setup

Ensure you have and activate the same environment before running the project. Run the following in the root directory of the project

### Using Conda (Recommended)

#### Create the Virtual Environment

```
conda create -n trading-simulator python=3.13
```

#### Activate the Environment

```
conda activate trading-simulator
```

#### Install Dependencies

```
pip install -r requirements.txt
```

### Alternative: Python venv (if no Conda)

#### Create the Virtual Environment

Mac/Linux:

```
python3.13 -m venv trading-simulator
```

Windows:

```
py -3.13 -m venv trading-simulator
```

#### Activate the Environment

Mac/Linux:

```
source trading-simulator/bin/activate
```

Windows:

```
source trading-simulator/Scripts/activate
```

#### Install Dependencies

```
pip install -r requirements.txt
```

## Generate Stubs

The generated gRPC Python files are not committed to the repository. After cloning the project, generate the client and server stubs by running:

```
./scripts/generate_stubs.sh
```

or 

```
python -m grpc_tools.protoc -I./proto --python_out=./generated --grpc_python_out=./generated ./proto/marketdata.proto ./proto/strategy.proto ./proto/execution.proto ./proto/portfolio.proto
```

# Architecture Overview

Market Data
      │
      ▼
Strategy
      │
      ▼
Execution
      │
      ▼
Portfolio

| Service     | Responsibility                                |
| ----------- | --------------------------------------------- |
| Market Data | Streams simulated price ticks                 |
| Strategy    | Consumes prices and generates trading signals |
| Execution   | Simulates order fills                         |
| Portfolio   | Tracks positions and PnL                      |
