# Quickstart Guide: Task Management Backend

## Prerequisites

- Python 3.11+
- pip package manager
- Access to Neon PostgreSQL database

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set up environment variables**
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update the values in `.env` with your actual configuration

7. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the application is running, you can access the automatic API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests

To run the tests:
```bash
pytest
```

To run tests with coverage:
```bash
pytest --cov=.
```

## Environment Variables

The application requires the following environment variables:

- `DATABASE_URL`: Connection string for the PostgreSQL database
- `BETTER_AUTH_SECRET`: Secret key for JWT token signing
- `BETTER_AUTH_URL`: URL for the Better Auth service

## API Endpoints

The backend provides the following endpoints:

- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Mark task as complete/incomplete

All endpoints require JWT authentication in the Authorization header.