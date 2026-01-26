# Banking API (FastAPI)

A backend banking API built with FastAPI as a **learning and practice project**, focused on applying real-world backend and security concepts such as authentication, authorization, account ownership, and safe transaction handling.

This project was created after completing a FastAPI course and then iteratively improved based on direct feedback from senior engineers, with particular emphasis on fixing common security mistakes seen in junior-level APIs.

---

## Features

- **JWT authentication** with secure token generation (`/auth/token`)
- **Secure password hashing** using bcrypt
- **Role-based access control** (user, admin)
- **One bank account per user** with strict ownership enforcement
- **Financial operations**: deposits, withdrawals, and transfers
- **Transaction history** with complete audit trail
- **Admin-only endpoints** for system-wide access
- **Server-side ownership enforcement** preventing unauthorized transfers
- **Environment-based configuration** for secure credential management
- **Precise financial calculations** using `Decimal` (no floating-point errors)

---

## Tech Stack

- **FastAPI** - Modern async web framework  
- **SQLAlchemy** - ORM and database toolkit  
- **SQLite** - Development database  
- **Alembic** - Database migrations  
- **JWT / OAuth2** - Authentication and authorization  
- **Uvicorn** - ASGI server  
- **python-dotenv** - Environment variable management  

---

## Security Features

- No hardcoded secrets - all sensitive values stored in environment variables  
- Proper `.gitignore` configuration - credentials and sensitive files never committed  
- Decimal precision for money - prevents floating-point errors  
- Transfer authorization - users can only transfer from accounts they own  
- Password hashing with bcrypt  
- JWT token expiry with configurable lifetime  
- Ownership enforced server-side using authenticated user context  

---

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
git clone https://github.com/jakub712/fastapi-banking-api.git
cd fastapi-banking-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
````

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./bankingApp.db
```

### Run the Application

```bash
uvicorn main:app --reload
```

API available at `http://localhost:8000`

---

## Core Endpoints

### Authentication

```
POST /auth/token
```

### Users

```
GET  /users/{username}
POST /users/create
```

### Accounts

```
POST /accounts/create/{user_id}
GET  /accounts/get_user/{username}
```

### Transactions

```
POST /transactions/deposit/{user_id}
POST /transactions/withdraw/{user_id}
POST /transactions/transfer/{from_user_id}/{to_user_id}
GET  /transactions/all/{account_id}
```

---

## Security Model

* All protected routes require a valid JWT
* Users can only access their own accounts
* Admin role required for elevated operations
* Authorization enforced at the API layer
* Transfers validate account ownership before execution
* No credentials stored in version control

---

## Improvements Based on Professional Feedback

**January 2025**

* Moved `SECRET_KEY` to environment variables
* Fixed `.gitignore` to prevent credential and database leaks
* Migrated all monetary values from `float` to `Decimal`
* Added strict ownership checks to prevent unauthorized transfers

---

## Purpose

This project was built as a hands-on learning exercise after completing a FastAPI course.

It demonstrates backend fundamentals such as authentication, authorization, data integrity, and API security, and shows how the project evolved through professional feedback.
