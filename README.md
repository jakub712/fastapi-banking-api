Banking API (FastAPI)

A backend-focused banking API built with FastAPI, implementing authentication, authorization, account ownership, and transaction handling.

This project is designed to demonstrate real backend responsibilities: secure access, role-based permissions, data integrity, and transactional logic.

Features

JWT authentication (/auth/token)

Secure password hashing

Role-based access control (user, admin)

One bank account per user

Deposits, withdrawals, and transfers

Transaction history

Admin-only endpoints for system-wide access

Server-side ownership enforcement

Tech Stack

FastAPI

SQLAlchemy

SQLite (development)

Alembic (migrations)

JWT / OAuth2

Uvicorn

Core Endpoints

Authentication

POST /auth/token


Users

GET /users/{username}
POST /users/create


Accounts

POST /accounts/create/{user_id}
GET  /accounts/get_user/{username}


Transactions

POST /transactions/deposit/{user_id}
POST /transactions/withdraw/{user_id}
POST /transactions/transfer/{from_user_id}/{to_user_id}
GET  /transactions/all/{account_id}

Security Model

All protected routes require a valid JWT

Users can only access their own accounts

Admin role required for elevated operations

Authorization enforced at the API layer

Purpose

This project focuses on backend correctness and system design rather than UI or deployment abstractions. It represents the type of application logic expected from a junior-to-mid backend engineer.
