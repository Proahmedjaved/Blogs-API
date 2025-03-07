# Blog API

A RESTful API for a blog application built with FastAPI, PostgreSQL, and Redis.

## Features

- User registration and authentication with JWT
- CRUD operations for blog posts
- Caching for read operations with Redis
- Containerized with Docker
- Reverse proxy with Nginx
- Comprehensive test coverage

## Requirements

- Python 3.12+
- uv (Python package manager)
- Docker and Docker Compose
- PostgreSQL
- Redis

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/blog-api.git
   cd blog-api
   ```

2. Install uv if you haven't already:
   ```bash
   pip install uv
   ```

3. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

4. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

## Running the Application

### Local Development

1. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. Start PostgreSQL and Redis (if running locally):
   ```bash
   # Start PostgreSQL
   sudo service postgresql start
   
   # Start Redis
   sudo service redis-server start
   ```

3. Run the application:
   ```bash
   uv run fastapi run --reload --host 0.0.0.0 --port 8000
   ```

### Using Docker

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. The API will be available at http://localhost:80

## Testing

1. Set up test environment:
   ```bash
   cp .env.test.example .env.test
   # Edit .env.test if needed
   ```

2. Run tests:
   ```bash
   # Run all tests
   uv run pytest

   # Run with coverage
   uv run pytest --cov=app --cov-report=term-missing --cov-report=html

   # Run specific test file
   uv run pytest tests/test_auth.py -v
   ```

3. View coverage report:
   ```bash
   # Open coverage_html/index.html in your browser
   ```

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:8000/docs (local) or http://localhost:80/docs (Docker)
- ReDoc: http://localhost:8000/redoc (local) or http://localhost:80/redoc (Docker)

## API Endpoints

### Authentication

- POST `/api/auth/register` - Register a new user
- POST `/api/auth/login` - Login and get access token

### Blog Posts

- GET `/api/posts/` - Get all blog posts
- POST `/api/posts/` - Create a new blog post (requires authentication)
- GET `/api/posts/{post_id}` - Get a specific blog post
- PUT `/api/posts/{post_id}` - Update a blog post (requires authentication)
- DELETE `/api/posts/{post_id}` - Delete a blog post (requires authentication)
- GET `/api/posts/me` - Get posts by the authenticated user (requires authentication)

## Development

### Project Structure