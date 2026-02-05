# 📊 Transaction Importer & Analytics Pipeline

A production-grade data engineering pipeline designed to handle high-frequency ingestion of financial transactions. It utilizes a **Hybrid Storage Strategy**: leveraging **Redis** for sub-millisecond real-time aggregation and **MongoDB** for reliable, long-term historical persistence.

## ✨ Features

### ⚡ High-Speed Ingestion

* **O(1) Aggregation** - Uses Redis `HINCRBYFLOAT` for sub-millisecond real-time daily totals.
* **Asynchronous Processing** - Decouples data ingestion from persistence using Redis lists as a high-speed message broker.
* **Bulk Persistence** - Minimizes MongoDB I/O overhead by grouping thousands of transactions into consolidated daily summaries via the background worker.

### 🛠️ Background Archiving

* **Automated Sync** - A dedicated worker service monitors the "hot" Redis cache and persists data to MongoDB every 10 seconds.
* **Smart Cleanup** - Automatically purges Redis keys older than 7 days to maintain a lean memory footprint.
* **Resilient Design** - Uses `asyncio` error handling to ensure the sync loop remains alive during network blips.

### 🐳 Infrastructure

* **Service Separation** - Multi-container setup separating HTTP (API), Background Worker, Cache (Redis), and Database (MongoDB).
* **Deterministic Environments** - Built with Docker and Pipenv (`Pipfile.lock`) to ensure consistent behavior across environments.

## 🏗️ System Architecture

1. **FastAPI App** receives transactions and validates data.
2. **Redis Queue** handles the message brokering while **Redis Stats** performs real-time aggregation.
3. **Background Worker** pulls from Redis and syncs to MongoDB every 10 seconds.
4. **MongoDB** acts as the final historical repository for aggregated daily stats.

## 📦 Tech Stack

| Component | Technology |
| --- | --- |
| **Backend Framework** | FastAPI (Python 3.12) |
| **Task Queue** | Redis (List-based Queue) |
| **Real-time Store** | Redis (Hashes for Daily Stats) |
| **Historical DB** | MongoDB (Document Store) |
| **Concurrency** | Asyncio, Motor (Async Mongo Driver) |
| **Orchestration** | Docker, Docker Compose |

## 📁 Project Structure

```text
FastAPI_transaction_importer/:
├── docker-compose.yml       # Infrastructure orchestration
├── Dockerfile               # Container definition
├── main.py                  # FastAPI Entry point
├── worker.py                # Async Sync & Cleanup Loop
├── database.py              # MongoDB/Motor configuration
├── redis_client.py          # Redis connection logic
├── models.py                # Data schemas
├── importer.py              # Data ingestion logic
├── transactions_1_month.csv # Sample dataset
├── Pipfile                  # Dependency management
└── .gitignore               # Version control exclusions

```

## 🚀 Quick Start (Local Deployment)

### 1. Installation

```bash
# Clone the repository 
git clone https://github.com/lamaDayoub/FastAPI_transaction_importer
cd FastAPI_transaction_importer

# Create environment file
cp .env.example .env

```

### 2. Launch Services & Ingest

Running the command below builds the environment and automatically triggers the data ingestion and worker synchronization. No further manual steps are required.

```bash
# Build and start services in the background
docker-compose up --build -d

```

## 🔍 Monitoring & API

### Watch Live Sync Logs

Monitor the worker's heartbeat and see the data being persisted in real-time:

```bash
docker logs -f transaction_importer-worker-1

```

### Database Verification

**Check MongoDB Collections:**

```bash
docker exec -it transaction_importer-mongodb-1 mongosh --eval "db.getSiblingDB('transaction_db').getCollectionNames()"

```

**Check API Documentation:**
Access Swagger UI to test endpoints: [http://localhost:8080/docs](https://www.google.com/search?q=http://localhost:8080/docs)

## 🐳 Docker Service Mapping

| Service | Container Port | Host Port | Description |
| --- | --- | --- | --- |
| `app` | 8000 | **8080** | FastAPI REST API |
| `worker` | -- | -- | Background Sync & Cleanup |
| `mongodb` | 27017 | **27017** | Permanent Document Store |
| `redis` | 6379 | **6379** | Message Broker & Cache |

---



