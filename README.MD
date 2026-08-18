# Library Service API

An online management system for a library's book borrowings, built with Django REST Framework.

## Features Implemented

| # | Task                                                              |
|---|-------------------------------------------------------------------|
| 1 | Books Service — CRUD for books                                    |
| 2 | Books Service — permissions (admin-only write, public read)       |
| 3 | Users Service — registration & JWT authentication                 |
| 4 | Borrowings Service — List & Detail endpoints                      |
| 5 | Borrowings Service — Create Borrowing endpoint                    |
| 6 | Payments Service — List & Detail endpoints                        |
| 7 | Payments Service — first manual Stripe Checkout Session           |
| 8 | Payments Service — automated Stripe Session creation on borrowing |

## Tech Stack

- Python / Django / Django REST Framework
- SQLite (local development) / PostgreSQL (Docker)
- JWT authentication via `djangorestframework-simplejwt`
- Stripe (`stripe` Python SDK) for payment sessions
- `python-dotenv` for environment configuration

## Resources / Data Model

**Book**
- `title`: str 
- `author`: str
- `cover`: Enum: `HARD` | `SOFT`
- `inventory`: positive int
- `daily_fee`: decimal (USD)

**User (Customer)**
- `email`: str 
- `first_name`: str 
- `last_name`: str 
- `password`: str 
- `is_staff`: bool

**Borrowing**
- `borrow_date`: date, auto-set on creation
- `expected_return_date`: date
- `actual_return_date`: date
- `book id`: int (FK)
- `user id`: int (FK)

**Payment**
- `status`: Enum: `PENDING` | `PAID`
- `type`: Enum: `PAYMENT` | `FINE`
- `borrowing id`: int (FK)
- `session_url`: url  # url to stripe payment session
- `session_id`: str  # id of stripe payment session
- `money_to_pay`: decimal (USD), calculated from the borrowing

## Getting Started

### 1. Clone and install dependencies

```bash
git clone https://github.com/B0hdanR/library-service.git
cd library-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Copy `.env.sample` to `.env` and fill in the values:

```bash
cp .env.sample .env
```

```env
SECRET_KEY=your_django_secret_key
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key

DEBUG=True

POSTGRES_DB=library_service
POSTGRES_USER=library_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

> `.env` is git-ignored — never commit real secrets. 
> `STRIPE_SECRET_KEY` must be a **test-mode** key (`sk_test_...`);
> PostgreSQL is used by default. To run locally without Docker (against SQLite instead), comment out the five POSTGRES_* lines above.

### 3. Run migrations and start the server

This uses SQLite for local development — comment out the `POSTGRES_*` variables in `.env` first, otherwise Django will try to connect to a `db` host that only exists inside Docker.
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API is available at `http://127.0.0.1:8000/api/doc/swagger/`.

### 4. Running with Docker

```bash
docker-compose build
docker-compose up
```

The app will be available at `http://127.0.0.1:8000/api/doc/swagger/`. Migrations run automatically on container startup.

To create an admin user:

```bash
docker-compose exec app python manage.py createsuperuser
```

## Authentication

JWT-based, via `djangorestframework-simplejwt`.

1. `POST /api/users/token/` with `email` and `password` → returns `access` and `refresh` tokens.
2. Pass the access token on subsequent requests: `Authorize: Bearer <token>`.
3. `POST /api/users/token/refresh/` to refresh an expired access token.

## API Endpoints

### Books

| Method    | Endpoint           | Description                     | Access     |
|-----------|--------------------|---------------------------------|------------|
| GET       | `/api/books/`      | List all books                  | Public     |
| GET       | `/api/books/<id>/` | Book detail                     | Public     |
| POST      | `/api/books/`      | Add a new book                  | Admin only |
| PUT/PATCH | `/api/books/<id>/` | Update a book (incl. inventory) | Admin only |
| DELETE    | `/api/books/<id>/` | Delete a book                   | Admin only |

### Users

| Method    | Endpoint                    | Description                      |
|-----------|-----------------------------|----------------------------------|
| POST      | `/api/users/`               | Register a new user              |
| POST      | `/api/users/token/`         | Obtain JWT access/refresh tokens |
| POST      | `/api/users/token/refresh/` | Refresh an access token          |
| GET       | `/api/users/me/`            | Get current user's profile       |
| PUT/PATCH | `/api/users/me/`            | Update current user's profile    |

### Borrowings

| Method | Endpoint                | Description                                                                                                            | Access                         |
|--------|-------------------------|------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| GET    | `/api/borrowings/`      | List borrowings (own only; admins see all)                                                                             | Authenticated                  |
| GET    | `/api/borrowings/<id>/` | Borrowing detail — includes full book info and any related payments                                                    | Authenticated (owner or admin) |
| POST   | `/api/borrowings/`      | Create a new borrowing — decreases book inventory by 1 and automatically creates a Stripe Checkout Session for payment | Authenticated                  |

Creating a borrowing also:
- Validates that `expected_return_date` is not in the past
- Validates that the book's inventory is not 0
- Attaches the current authenticated user automatically
- Calculates the borrowing's total price (`days × daily_fee`) and creates a Stripe test-mode Checkout Session for it
- Creates a `Payment` record (`status=PENDING`, `type=PAYMENT`) linked to the borrowing, storing the Stripe `session_url` and `session_id`

### Payments

| Method | Endpoint              | Description                                                     | Access                         |
|--------|-----------------------|-----------------------------------------------------------------|--------------------------------|
| GET    | `/api/payments/`      | List payments (own only; admins see all)                        | Authenticated                  |
| GET    | `/api/payments/<id>/` | Payment detail — includes Stripe `session_url` and `session_id` | Authenticated (owner or admin) |

Payments are never created or modified directly through this endpoint — they're generated automatically when a borrowing is created. This endpoint is read-only.

## Stripe Integration

- Uses Stripe's **test mode**.
- On borrowing creation, a Checkout Session is created via `stripe.checkout.Session.create()` with:
  - `line_items` — one item, `quantity=1`, `unit_amount` set from the calculated borrowing price (converted to cents)
  - `mode="payment"`
  - Placeholder `success_url` / `cancel_url` (not yet wired to real confirmation endpoints in this submission)

## Testing

Run the test suite:

```bash
python manage.py test
```

Custom functionality (models, serializers, views) for Books, Users, Borrowings, and Payments is covered by unit tests, including:
- Model validation and constraints
- Serializer field visibility and read-only enforcement
- Permission checks (owner, admin, unauthenticated)
- The full borrowing-creation flow, with the Stripe API call mocked (`unittest.mock.patch`) so tests run without a real Stripe key

Run the coverage suite:

```bash
coverage run manage.py test
coverage report
```

Test coverage target: 99% of custom code.

## Project Structure

```
library_service/
├── books/            # Books CRUD + permissions
├── borrowings/       # Borrowing creation, list & detail
├── library_service/  # project settings
├── payments/         # Payment model, list & detail, Stripe integration
│   └── stripe_service.py   # helper for creating Stripe Checkout Sessions
├── users/            # User registration & JWT auth
├── .env.sample
├── .flake8
├── .gitignore
├── manage.py
├── README.MD
└── requirements.txt
```
