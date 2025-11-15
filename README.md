# FastAPI Product Management API

RESTful API service dengan Python FastAPI untuk management lengkap users, products, categories, dan roles dengan JWT authentication. Menggunakan PostgreSQL sebagai database utama dengan dukungan pagination metadata, sorting, dan stock status indicator.

## Fitur Utama

- **Authentication**: JWT-based login, logout, dan register dengan role-based access dan auto-login setelah registrasi
- **User Management**: CRUD users dengan role system (PostgreSQL)
  - ✅ Pagination dengan metadata (total count, page info)
  - ✅ Sorting (by username, email, full_name, created_at)
  - ✅ Enhanced search (username, email, full_name)
- **Product Management**: CRUD products dengan category relations (PostgreSQL)
  - ✅ Pagination dengan metadata (total count, page info)
  - ✅ Sorting (by name, stock, price, created_at, status)
  - ✅ Stock status indicator (red/yellow/green)
- **Category Management**: CRUD categories untuk products (PostgreSQL)
- **Role Management**: Management roles untuk user permissions (PostgreSQL)
- **Data Validation**: Pydantic schema validation
- **API Documentation**: Swagger UI dan ReDoc
- **Async/Await**: Full async support untuk performa optimal
- **Error Handling**: Comprehensive error handling dengan global exception handler
- **Health Check**: Endpoint untuk monitoring
- **CORS**: CORS middleware configured
- **Auto Database Init**: Automatic database schema creation on startup

> **Note**: Book Management (MongoDB) feature is currently disabled

## Tech Stack

- **FastAPI** 0.109.0 - Modern Python web framework
- **PostgreSQL** - Relational database untuk users, products, categories, roles
- **MongoDB Atlas** - NoSQL database (optional, currently disabled)
- **SQLAlchemy** 2.0.25 - Async ORM untuk PostgreSQL
- **Motor** 3.3.2 - Async MongoDB driver
- **JWT** - JSON Web Tokens untuk authentication (python-jose)
- **Pydantic** 2.5.3 - Data validation
- **Passlib + Bcrypt** - Password hashing
- **Uvicorn** - ASGI server
- **Supabase** - Optional cloud database integration

## Prerequisites

- Python 3.11+
- PostgreSQL database
- MongoDB Atlas account (optional, currently not in use)
- pip (Python package manager)

## Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd api-fullstack-initial
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` ke `.env` dan update dengan credentials Anda:

```env
# --- App Info ---
APP_NAME=FastAPI Product Management API
VERSION=1.0.0
API_V1_PREFIX=/api/v1

# --- Auth ---
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=240

# --- PostgreSQL ---
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=your-host.sql
POSTGRES_PORT=5432
POSTGRES_DB=your_database_name

# --- MongoDB ---
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net
MONGODB_DB_NAME=bookstore

# --- Supabase (Optional) ---
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key

# --- CORS ---
CORS_ORIGINS=["*"]
```

### 4. Run Application

**Development Mode:**

```bash
# Option 1: Using run.py
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server akan berjalan di: `http://localhost:8000`

### 5. Database Initialization

Database schema akan otomatis dibuat saat aplikasi pertama kali dijalankan. Roles default (admin, user) akan di-seed otomatis.

## API Documentation

Setelah aplikasi berjalan, akses:

- **Swagger UI (Interactive)**: http://localhost:8000/docs
- **ReDoc (Alternative)**: http://localhost:8000/redoc
- **Root Endpoint**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Root & Health

```
GET  /                    - Welcome message & API info
GET  /health              - Health check endpoint
```

### Authentication

```
POST /api/v1/auth/register - Register account baru
POST /api/v1/auth/login    - Login dan dapatkan JWT token
GET  /api/v1/auth/me       - Get current user info
POST /api/v1/auth/logout   - Logout user
```

### Users (Requires Authentication)

```
GET    /api/v1/users          - Get all users (with pagination, sorting, filtering & metadata)
GET    /api/v1/users/{id}     - Get user detail by ID
POST   /api/v1/users          - Create new user
PUT    /api/v1/users/{id}     - Update user
DELETE /api/v1/users/{id}     - Delete user
```

**Response Format (GET /api/v1/users):**
```json
{
  "data": [{ /* user objects */ }],
  "metadata": {
    "total": 45,
    "skip": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 5
  }
}
```

### Products (Requires Authentication)

```
GET    /api/v1/products       - Get all products (with pagination, sorting, filtering & metadata)
GET    /api/v1/products/{id}  - Get product detail (includes stock_status)
POST   /api/v1/products       - Create product
PUT    /api/v1/products/{id}  - Update product
DELETE /api/v1/products/{id}  - Delete product
```

**Response Format (GET /api/v1/products):**
```json
{
  "data": [{
    "id": "...",
    "name": "Gaming Laptop",
    "stock": 5,
    "stock_status": "yellow",  // red | yellow | green
    /* ... */
  }],
  "metadata": {
    "total": 156,
    "skip": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 16
  }
}
```

### Categories (Requires Authentication)

```
GET    /api/v1/categories       - Get all categories (with pagination & filtering)
GET    /api/v1/categories/{id}  - Get category detail
POST   /api/v1/categories       - Create category
PUT    /api/v1/categories/{id}  - Update category (only creator)
DELETE /api/v1/categories/{id}  - Delete category
```

### Roles (Requires Authentication)

```
GET    /api/v1/roles       - Get all roles (with pagination & filtering)
GET    /api/v1/roles/{id}  - Get role detail
POST   /api/v1/roles       - Create role
PUT    /api/v1/roles/{id}  - Update role
DELETE /api/v1/roles/{id}  - Delete role
```

> **Note**: Books endpoints are currently disabled

## Query Parameters

### Pagination (All List Endpoints)

- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 10, max: 100)

### Sorting

**Users:**
- `sort_by`: Field to sort by: `username`, `email`, `full_name`, `created_at`
- `order`: Sort order: `asc` (ascending) or `desc` (descending) - default: `asc`

**Products:**
- `sort_by`: Field to sort by: `name`, `stock`, `price`, `created_at`, `status`
- `order`: Sort order: `asc` (ascending) or `desc` (descending) - default: `asc`
  - When `sort_by=status`: `asc` = red → yellow → green (urgent first), `desc` = green → yellow → red

### Filtering

**Users:**
- `search`: Search by username, email, or full name (case-insensitive, partial match)

**Products:**
- `search`: Search by product name
- `category_id`: Filter by category UUID

**Categories:**
- `search`: Search by category name

**Roles:**
- `search`: Search by role name

## Usage Examples

### 1. Register New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "password": "SecurePassword123",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "metadata": {
    "id": "uuid-here",
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "role": {
      "id": "user",
      "name": "user",
      "description": "Regular user with basic permissions"
    }
  }
}
```

> **Note**: Register endpoint now auto-logins the user and returns an access token

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=SecurePassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "metadata": {
    "id": "uuid-here",
    "email": "john@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "role": {
      "id": "user",
      "name": "user",
      "description": "Regular user with basic permissions"
    }
  }
}
```

### 3. Get Current User Info

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Create Category

```bash
curl -X POST "http://localhost:8000/api/v1/categories" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }'
```

### 5. Create Product

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15 Pro",
    "description": "Latest Apple smartphone with A17 Pro chip",
    "price": 999.99,
    "stock": 50,
    "low_stock_threshold": 10,
    "image_url": "https://example.com/iphone15.jpg",
    "category_id": "category-uuid-here"
  }'
```

### 6. Get Products with Filtering and Sorting

```bash
# Basic filtering with sorting by price (lowest first)
curl "http://localhost:8000/api/v1/products?search=iphone&category_id=category-uuid&sort_by=price&order=asc&skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Sort by stock status (urgent products first: red → yellow → green)
curl "http://localhost:8000/api/v1/products?sort_by=status&order=asc&skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": "...",
      "name": "Product A",
      "stock": 0,
      "stock_status": "red",
      "price": 999.99,
      ...
    }
  ],
  "metadata": {
    "total": 156,
    "skip": 0,
    "limit": 20,
    "page": 1,
    "total_pages": 8
  }
}
```

### 7. Get Users with Sorting

```bash
# Sort users by registration date (newest first)
curl "http://localhost:8000/api/v1/users?sort_by=created_at&order=desc&skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search users and sort alphabetically
curl "http://localhost:8000/api/v1/users?search=john&sort_by=username&order=asc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": "...",
      "username": "johndoe",
      "email": "john@example.com",
      ...
    }
  ],
  "metadata": {
    "total": 15,
    "skip": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 2
  }
}
```

## Project Structure

```
api-fullstack-initial/
├── api/
│   └── index.py                 # Vercel serverless entry point
├── app/
│   ├── config.py                # Configuration settings & environment variables
│   ├── database.py              # Database connections (PostgreSQL + MongoDB)
│   ├── dependencies.py          # FastAPI dependencies (auth, DB sessions)
│   ├── main.py                  # FastAPI application entry point
│   ├── seed_data.py             # Database seeding (roles initialization)
│   ├── models/
│   │   ├── user.py              # SQLAlchemy User model
│   │   ├── product.py           # SQLAlchemy Product model
│   │   ├── category.py          # SQLAlchemy Category model
│   │   └── role.py              # SQLAlchemy Role model
│   ├── routers/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── users.py             # Users CRUD endpoints (enhanced with sorting)
│   │   ├── products.py          # Products CRUD endpoints (enhanced with sorting & stock status)
│   │   ├── categories.py        # Categories CRUD endpoints
│   │   ├── books.py             # Books CRUD endpoints (currently disabled)
│   │   └── roles.py             # Roles CRUD endpoints
│   ├── schemas/
│   │   ├── auth.py              # Auth Pydantic schemas (login, register)
│   │   ├── user.py              # User Pydantic schemas
│   │   ├── product.py           # Product Pydantic schemas
│   │   ├── category.py          # Category Pydantic schemas
│   │   ├── book.py              # Book Pydantic schemas
│   │   └── role.py              # Role Pydantic schemas
│   └── utils/
│       └── security.py          # JWT & password utilities
├── run.py                       # Development server runner
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker container configuration
├── vercel.json                  # Vercel deployment configuration
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Database Schema

### PostgreSQL Tables

**users**
- id (UUID, Primary Key)
- email (String, Unique)
- username (String, Unique)
- hashed_password (String)
- full_name (String)
- is_active (Boolean)
- role_id (String, Foreign Key to roles)
- created_at (DateTime)
- updated_at (DateTime)

**products**
- id (UUID, Primary Key)
- name (String)
- description (Text, Optional)
- price (Decimal)
- stock (Integer)
- low_stock_threshold (Integer)
- image_url (String, Optional)
- category_id (UUID, Foreign Key to categories)
- created_by (UUID, Foreign Key to users)
- created_at (DateTime)
- updated_at (DateTime)

**categories**
- id (UUID, Primary Key)
- name (String, Unique)
- description (Text, Optional)
- created_by (UUID, Foreign Key to users)
- created_at (DateTime)
- updated_at (DateTime)

**roles**
- id (String, Primary Key)
- name (String, Unique)
- description (Text, Optional)
- created_at (DateTime)
- updated_at (DateTime)

> **Note**: MongoDB collections (books) are currently not in use

## Security

- **Password Hashing**: Passwords di-hash menggunakan bcrypt dengan salt
- **JWT Tokens**: Authentication menggunakan JWT dengan expiration time
- **Token Expiration**: Default 240 menit (4 jam), bisa dikonfigurasi via env
- **Logout Behavior**: Token tetap valid hingga expiry meskipun sudah logout (active token tracking saat ini dinonaktifkan)
- **CORS**: CORS middleware configured untuk cross-origin requests
- **Input Validation**: Semua input divalidasi dengan Pydantic schemas
- **SQL Injection Protection**: SQLAlchemy ORM mencegah SQL injection
- **Authorization**: Role-based access control untuk endpoints tertentu
- **Owner Verification**: Category update/delete hanya bisa dilakukan oleh creator

> **Security Note**: Untuk production deployment, pertimbangkan untuk mengaktifkan token blacklist atau database token storage untuk true logout functionality

## Error Handling

API mengembalikan error responses dalam format JSON standar:

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource successfully created
- `204 No Content`: Success with no response body (delete)
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Not authorized to perform action
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Development

### Running in Development Mode

```bash
# With auto-reload
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload --log-level debug
```

### Testing API Endpoints

1. **Swagger UI** (`/docs`) - Interactive API testing dengan UI
2. **ReDoc** (`/redoc`) - Alternative documentation viewer
3. **cURL** - Command line testing (lihat contoh di atas)
4. **Postman** - Import OpenAPI schema dari `/docs`
5. **HTTPie** - Modern command line HTTP client

### Code Style & Best Practices

- Async/await untuk semua database operations
- Type hints untuk semua function parameters dan returns
- Pydantic models untuk validation dan serialization
- Proper error handling dengan HTTP exceptions
- Clean separation of concerns (models, schemas, routers)
- Environment-based configuration
- Dependency injection pattern

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t fastapi-product-api .

# Run container
docker run -d -p 8080:8080 \
  --env-file .env \
  --name product-api \
  fastapi-product-api
```

### Vercel Deployment

Project sudah dikonfigurasi untuk deployment di Vercel:

1. Push code ke GitHub repository
2. Import project di Vercel dashboard
3. Configure environment variables di Vercel settings
4. Deploy otomatis akan berjalan

```json
// vercel.json already configured
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ]
}
```

### Cloud Run / Docker Deployment

```bash
# Build dan push ke Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/product-api

# Deploy ke Cloud Run
gcloud run deploy product-api \
  --image gcr.io/PROJECT_ID/product-api \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --port 8080
```

### Production Checklist

- [ ] Update `SECRET_KEY` dengan strong random key (min 32 characters)
- [ ] Set proper `ACCESS_TOKEN_EXPIRE_MINUTES` (recommended: 30-60)
- [ ] Configure specific `CORS_ORIGINS` (jangan gunakan "*" di production)
- [ ] Use production database credentials dengan strong passwords
- [ ] Enable HTTPS/SSL
- [ ] Setup proper logging dan monitoring
- [ ] Configure database backups
- [ ] Set up CI/CD pipeline
- [ ] Implement rate limiting
- [ ] Add request logging middleware
- [ ] Configure production-ready error tracking (Sentry, etc.)
- [ ] Use environment variables untuk semua sensitive data
- [ ] Disable debug mode
- [ ] Implement database migrations (Alembic)

### Database Migrations (Alembic)

Untuk production deployment dengan controlled migrations:

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Configure alembic.ini dengan database URL

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_NAME` | No | FastAPI Product Management API | Application name |
| `VERSION` | No | 1.0.0 | API version |
| `API_V1_PREFIX` | No | /api/v1 | API route prefix |
| `SECRET_KEY` | Yes | - | JWT secret key |
| `ALGORITHM` | No | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | 240 | Token expiration |
| `POSTGRES_USER` | Yes | - | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | - | PostgreSQL password |
| `POSTGRES_HOST` | Yes | - | PostgreSQL host |
| `POSTGRES_PORT` | No | 5432 | PostgreSQL port |
| `POSTGRES_DB` | Yes | - | PostgreSQL database name |
| `MONGODB_URL` | Yes | - | MongoDB connection string |
| `MONGODB_DB_NAME` | Yes | - | MongoDB database name |
| `SUPABASE_URL` | No | - | Supabase project URL |
| `SUPABASE_KEY` | No | - | Supabase API key |
| `CORS_ORIGINS` | No | ["*"] | Allowed CORS origins |

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL connection
psql -h POSTGRES_HOST -U POSTGRES_USER -d POSTGRES_DB

# Test MongoDB connection
mongosh "MONGODB_URL"
```

### Common Errors

**"Could not connect to PostgreSQL"**
- Verify POSTGRES_* environment variables
- Check network connectivity
- Ensure PostgreSQL is running

**"Could not connect to MongoDB"**
- Verify MONGODB_URL format
- Check MongoDB Atlas IP whitelist
- Ensure cluster is running

**"Invalid authentication token"**
- Token might be expired
- Check SECRET_KEY configuration
- Re-login to get new token

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - feel free to use this project for your own purposes.

## Support

Untuk pertanyaan atau issues:
- Create GitHub issue
- Contact maintainer

## Changelog

### Version 1.0.1 (Current)
- **Enhanced Users API**:
  - Pagination dengan metadata (total count, page info)
  - Sorting by username, email, full_name, created_at
  - Enhanced search across username, email, and full_name
- **Enhanced Products API**:
  - Pagination dengan metadata (total count, page info)
  - Sorting by name, stock, price, created_at, status
  - Stock status indicator (red/yellow/green)
- **Disabled** Books management (MongoDB) temporarily

### Version 1.0.0
- Initial release
- User management dengan role system
- Product & Category management
- JWT authentication
- Full CRUD operations
- Basic pagination & filtering
- Auto database initialization
- Health check endpoint
- Comprehensive error handling
