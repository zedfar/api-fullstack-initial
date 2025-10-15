# FastAPI Book Management API

RESTful API service dengan Python FastAPI untuk management users dan buku dengan JWT authentication.

## Fitur

- **Authentication**: JWT-based login, logout, dan register
- **CRUD Users**: Management pengguna dengan PostgreSQL
- **CRUD Books**: Management buku dengan MongoDB Atlas
- **Pagination & Filtering**: Support pagination dan filtering untuk semua list endpoints
- **Data Validation**: Pydantic schema validation
- **API Documentation**: Swagger UI dan ReDoc
- **Async/Await**: Full async support untuk performa optimal
- **Error Handling**: Comprehensive error handling
- **Health Check**: Endpoint untuk monitoring
- **CORS**: CORS middleware configured

## Tech Stack

- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database untuk users (Google Cloud SQL)
- **MongoDB**: NoSQL database untuk books (MongoDB Atlas)
- **JWT**: JSON Web Tokens untuk authentication
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM untuk PostgreSQL
- **Motor**: Async MongoDB driver

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` ke `.env` dan update dengan credentials Anda:

```env
SECRET_KEY=your-secret-key-here
MONGODB_URL=mongodb
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=your-host.sql
POSTGRES_DB=dbname
```

### 3. Initialize Database

```bash
python init_db.py
```

### 4. Run Application

```bash
python main.py
```

atau dengan uvicorn:

```bash
uvicorn main:app --reload
```

Server akan berjalan di: `http://localhost:8000`

## API Documentation

Setelah aplikasi berjalan, akses:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```
GET /health
```

### Authentication

```
POST /api/v1/auth/register - Register account baru
POST /api/v1/auth/login - Login dan dapatkan JWT token
POST /api/v1/auth/logout - Logout user
```

### Users (Requires Authentication)

```
GET    /api/v1/users - Get all users (with pagination & filtering)
GET    /api/v1/users/{id} - Get user detail
POST   /api/v1/users - Create user
PUT    /api/v1/users/{id} - Update user
DELETE /api/v1/users/{id} - Delete user
```

### Books (Requires Authentication)

```
GET    /api/v1/books - Get all books (with pagination & filtering)
GET    /api/v1/books/{id} - Get book detail
POST   /api/v1/books - Create book
PUT    /api/v1/books/{id} - Update book
DELETE /api/v1/books/{id} - Delete book
```

## Query Parameters

### Pagination

- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 10, max: 100)

### Filtering

**Users:**
- `search`: Search by username or email

**Books:**
- `search`: Search by title or author
- `author`: Filter by author
- `min_price`: Minimum price
- `max_price`: Maximum price

## Usage Examples

### 1. Register

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "password123",
    "full_name": "John Doe"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=password123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Create Book (with authentication)

```bash
curl -X POST "http://localhost:8000/api/v1/books" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "description": "A Handbook of Agile Software Craftsmanship",
    "isbn": "978-0132350884",
    "published_year": 2008,
    "price": 45.99
  }'
```

### 4. Get Books with Filtering

```bash
curl "http://localhost:8000/api/v1/books?search=clean&min_price=20&max_price=50&skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connections
│   ├── dependencies.py        # FastAPI dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py            # SQLAlchemy User model
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # Users CRUD endpoints
│   │   └── books.py           # Books CRUD endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # User Pydantic schemas
│   │   ├── book.py            # Book Pydantic schemas
│   │   └── auth.py            # Auth Pydantic schemas
│   └── utils/
│       ├── __init__.py
│       └── security.py        # JWT & password utilities
├── main.py                    # FastAPI application entry point
├── init_db.py                 # Database initialization script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .env.example              # Environment variables example
└── README.md                 # Documentation
```

## Security

- Passwords di-hash menggunakan bcrypt
- JWT tokens untuk authentication
- Token expiration configured (default: 30 minutes)
- CORS middleware untuk cross-origin requests
- Input validation dengan Pydantic

## Error Handling

API mengembalikan error responses dalam format JSON:

```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

## Development

### Testing

Gunakan Swagger UI (`/docs`) untuk testing endpoints interaktif.

### Database Migrations

Untuk production, gunakan Alembic untuk database migrations:

```bash
pip install alembic
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Production Deployment

1. Update `SECRET_KEY` di `.env` dengan strong random key
2. Set `ACCESS_TOKEN_EXPIRE_MINUTES` sesuai kebutuhan
3. Configure proper CORS origins di `config.py`
4. Use production database credentials
5. Enable HTTPS
6. Setup proper logging
7. Use process manager (e.g., systemd, supervisor)
8. Consider using Gunicorn with Uvicorn workers:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## License

MIT
