# Wallet API

REST API for managing digital wallets. The application supports balance retrieval, deposits, and withdrawals with concurrency protection.

## Technologies

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0
- Alembic
- Pydantic
- Docker & Docker Compose
- Pytest
- HTTPX

## Features

- Retrieve wallet balance.
- Deposit funds into a wallet.
- Withdraw funds from a wallet.
- Validate operation amounts.
- Prevent negative wallet balances.
- Handle concurrent operations using database transactions and row-level locking.
- Manage database schema through Alembic migrations.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/lis0leg/wallet-api.git
cd wallet-api
```

### 2. Configure environment variables

Create a `.env` file based on `.env.example`.

```bash
cp .env.example .env
```

Set your PostgreSQL password in `.env`.

### 3. Start the application

```bash
docker compose up --build
```

Docker Compose starts PostgreSQL, waits for database readiness, applies Alembic migrations, and launches the FastAPI application.

### 4. Open Swagger UI

http://localhost:8000/docs

## API Endpoints

### Get wallet balance

`GET /api/v1/wallets/{wallet_id}`

Returns the current wallet balance.

Example response:

```json
{
  "id": "wallet-uuid",
  "balance": "1000.00"
}
```

### Perform wallet operation

`POST /api/v1/wallets/{wallet_id}/operation`

Request body:

```json
{
  "operation_type": "DEPOSIT",
  "amount": 1000
}
```

Supported operation types:

- `DEPOSIT` — add funds.
- `WITHDRAW` — withdraw funds.

Example response:

```json
{
  "id": "wallet-uuid",
  "balance": "1000.00"
}
```

## Error Handling

- `404 Not Found` — wallet does not exist.
- `409 Conflict` — insufficient funds.
- `422 Unprocessable Entity` — invalid request data.

## Concurrency

Wallet balance modifications are protected using PostgreSQL transactions and `SELECT FOR UPDATE`.

This prevents concurrent operations from incorrectly modifying the same wallet balance.

A database constraint also prevents balances from becoming negative.

## Running Tests

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create the test database if it does not exist:

```bash
docker compose exec db psql -U wallet_user -d wallet_db
```

Then execute:

```sql
CREATE DATABASE wallet_test_db;
```

Run tests:

```bash
python -m pytest -v
```

## Database Migrations

Apply migrations:

```bash
alembic upgrade head
```

Generate a new migration:

```bash
alembic revision --autogenerate -m "migration description"
```