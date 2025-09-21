# FastAPI Task Manager

## Description

This is a simple but functional Task Manager API built with FastAPI and SQLAlchemy. It provides a RESTful interface for managing tasks, with endpoints for creating and listing them. The project demonstrates a clean separation of concerns using Pydantic for data validation and SQLAlchemy for database interactions.

## Features

- **Create Tasks:** Add new tasks with a title, completion status, and priority.
- **List All Tasks:** Retrieve a list of all tasks stored in the database.
- **Data Validation:** Automatic request and response data validation using Pydantic models.
- **Database ORM:** Uses SQLAlchemy to interact with a SQLite database.
- **Auto-generated Docs:** Built-in interactive API documentation with Swagger UI (at `/docs`).

## Setup and Run

### Prerequisites

- Python 3.8+
- `pip` (Python package installer)

### Installation

1.  **Clone the repository:**

    ```sh
    git clone https://github.com/yoftil7/FastAPI-Task-Manager-with-DB.git
    cd task_manager_fastapi
    ```

2.  **Create and activate a virtual environment** (recommended):

    ```sh
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # or
    .\venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```sh
    pip install fastapi "uvicorn[standard]" sqlalchemy "pydantic[extra]"
    ```

4.  **Run the application:**
    ```sh
    uvicorn main:app --reload
    ```

### Usage

Once the server is running, you can access the interactive API documentation by navigating to `http://127.0.0.1:8000/docs` in your web browser. From there, you can explore and test the available endpoints.

## Project Structure

- `main.py`: The main FastAPI application file where endpoints are defined.
- `database.py`: Contains the database engine and session setup.
- `models.py`: Defines the SQLAlchemy ORM models for database tables.
- `schemas.py`: Defines the Pydantic models for data validation and serialization.
- `tasks.db`: The SQLite database file (ignored by Git).
- `venv/`: The virtual environment directory (ignored by Git).

## Planned Enhancements

- [ ] Add CRUD operations: Get by ID, update, and delete tasks.
- [ ] Implement database migrations (e.g., using Alembic) for managing schema changes.
- [ ] Add unit and integration tests.
- [ ] Incorporate user authentication.

## License

This project is licensed under the MIT License.
