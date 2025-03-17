# Senior Project Backend

## Features

* Student transcript extraction

* Graduation eligibility determination

* PDF report generation

* REST API with FastAPI

* PostgreSQL database integration

## Getting Started

### 1. Prerequisites

Ensure you have Docker installed.

### 2. Clone the Repository
```
git clone https://github.com/Boost-Oat-SeniorProject/SeniorProjectBackend.git
cd SeniorProjectBackend
```
### 3. Set up Environment Variables

Create a .env file in the root directory with the following:
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/test
POSTGRES_PASSWORD=postgres
POSTGRES_USER=postgres
POSTGRES_DB=test
FRONTEND_URL=http://localhost:3000
```
### 4. Start the Backend with Docker
Run the following command:
```
docker-compose up --build
```
### 5. Access API Documentation

Once the server is running, visit:

Swagger UI: http://localhost:8000/docs
