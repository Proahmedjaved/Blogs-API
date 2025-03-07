# Blog API

A RESTful API for a blog application built with FastAPI, PostgreSQL, and Redis.

## Features

- User registration and authentication with JWT
- CRUD operations for blog posts
- Caching for read operations with Redis
- Containerized with Docker
- Reverse proxy with Nginx

## Requirements

- Docker and Docker Compose

## Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/blog-api.git
   cd blog-api
   ```

2. Start the application with Docker Compose:
   ```
   docker-compose up -d
   ```

3. The API is now available at http://localhost:80

## API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://localhost:80/docs
- ReDoc: http://localhost:80/redoc

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

## Running Tests 