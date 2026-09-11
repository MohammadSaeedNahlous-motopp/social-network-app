# Social Network API

A RESTful social network backend built with **FastAPI** and **SQLAlchemy**.

The project provides API functionality for user authentication, user management, posts, friendships, friend requests, groups, and group memberships. It is structured as a modular backend application with separate layers for API routing, data models, schemas, database access, and business logic.

## Features

- User registration and authentication
- Password hashing and JWT-based authentication
- User management
- Create and manage posts
- Image upload and processing
- Send and manage friend requests
- Manage friendships
- Create and manage groups
- Manage group memberships and roles
- SQLAlchemy-based database access
- Pydantic request and response validation
- Automated tests with `pytest`
- Test coverage support with `pytest-cov`
- Code quality tooling with Ruff
- GitHub Actions workflow for automated testing

## Tech Stack

| Technology | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework and REST API |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server |
| [SQLAlchemy](https://www.sqlalchemy.org/) | Database ORM |
| [Pydantic](https://docs.pydantic.dev/) | Data validation and schemas |
| [python-jose](https://python-jose.readthedocs.io/) | JWT handling |
| [pwdlib](https://frankie567.github.io/pwdlib/) | Password hashing |
| [Pillow](https://python-pillow.org/) | Image processing |
| [pytest](https://docs.pytest.org/) | Automated testing |
| [pytest-cov](https://pytest-cov.readthedocs.io/) | Test coverage |
| [Ruff](https://docs.astral.sh/ruff/) | Linting and code quality |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | Environment configuration |

The dependencies above are based on the project's current `requirements.txt`.

## Project Structure

```text
social-network-app/
│
├── .github/
│   └── workflows/
│       └── tests.yaml
│
├── auth/
│   └── ...
│
├── db/
│   └── ...
│
├── models/
│   └── ...
│
├── routers/
│   ├── authentication.py
│   ├── user.py 
│   ├── post_group.py
│   ├── post.py
│   ├── friend_request.py
│   ├── friend.py
│   ├── group.py
│   └── group_member.py
│
├── schemas/
│   └── ...
│
├── service/
│   └── ...
│
├── tests/
│   ├── auth_tests/
│   ├── friend_request_tests/
│   ├── friend_tests/
│   ├── group_tests/
│   ├── image_service_tests/
│   ├── membership_tests/
│   ├── user_tests/
│   └── ...
│
├── .example.env
├── .gitignore
├── main.py
├── pyproject.toml
└── requirements.txt
```

The project separates API endpoints from database models, schemas, and service logic. The `routers` package currently contains dedicated modules for authentication, users, posts, friend requests, friends, groups, and group members.

The `tests` directory follows a similar feature-oriented organization, with dedicated test modules for authentication, users, friendships, friend requests, groups, memberships, posts, and image services.

### Directory responsibilities

#### `auth/`

Contains authentication-related functionality used by the API.

#### `db/`

Contains database configuration, SQLAlchemy setup, sessions, and database initialization/seed functionality.

#### `models/`

Contains SQLAlchemy database models representing the application's persistent data.

#### `schemas/`

Contains Pydantic models used for validating API input and serializing API responses.

#### `routers/`

Contains FastAPI route handlers. Each module groups endpoints belonging to a particular feature.

#### `service/`

Contains reusable business logic that should not be tightly coupled to individual API route handlers.

#### `tests/`

Contains automated tests organized by application feature.

#### `.github/workflows/`

Contains GitHub Actions workflows used for automated project checks. The current branch includes a test workflow.

## Prerequisites

Before setting up the project, make sure the following are installed:

- Python 3.x
- `pip`
- Git

You can verify your Python installation with:

```bash
python --version
```

## Installation

Clone the repository:

```bash
git clone https://github.com/MohammadSaeedNahlous-motopp/social-network-app.git
cd social-network-app
```

Switch to the development branch:

```bash
git checkout development
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The application uses environment variables for configuration.

Create a `.env` file based on the provided example:

```bash
cp .example.env .env
```

On Windows, you can create `.env` manually by copying `.example.env`.

The current example configuration contains:

```env
AUTH_SECRET_KEY=
```

Set `AUTH_SECRET_KEY` to a secure, randomly generated value before running the application. The example environment file is intentionally provided without a secret value.

> **Important:** Never commit your real `.env` file or authentication secrets to the repository.

## Running the Application

Start the development server with Uvicorn:

```bash
uvicorn main:app --reload
```

The `--reload` option automatically restarts the development server when source files are changed.

Once the server is running, the API will be available at:

```text
http://127.0.0.1:8000
```

The application's FastAPI instance and routers are initialized in `main.py`. The application currently registers the authentication, user, post, friend request, friend, group, and group member routers when it starts.

## API Documentation

FastAPI automatically generates interactive API documentation.

After starting the server, open:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger UI provides an interactive interface for exploring and testing the available API endpoints.

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

ReDoc provides an alternative, documentation-oriented view of the OpenAPI specification.

The interactive documentation should be considered the primary reference for the exact request parameters, response schemas, and available endpoints.

## API Functionality

The API is organized around several main features.

### Authentication

Authentication endpoints are implemented in:

```text
routers/authentication.py
```

Authentication uses password hashing and JWT-based access tokens.

### Users

User-related endpoints are implemented in:

```text
routers/user.py
```

These endpoints handle operations related to user accounts and profiles.

### Posts and group posts

Post functionality is implemented in:

```text
routers/post.py
```
and
```text
routers/post_group.py
```

The project also contains image-processing functionality used by the application.

### Friend Requests

Friend request functionality is separated into:

```text
routers/friend_request.py
```

This handles the lifecycle of requests between users.

### Friends

Friendship functionality is implemented in:

```text
routers/friend.py
```

### Groups

Group-related operations are implemented in:

```text
routers/group.py
```

### Group Memberships

Membership-related operations are implemented separately in:

```text
routers/group_member.py
```

This separation keeps group management and membership operations independent at the API level.

## Testing

The project uses `pytest` for automated tests.

Run the complete test suite with:

```bash
python -m pytest -v
```

The repository also includes test coverage support:

```bash
pytest --cov
```

Tests are organized by feature, including authentication, users, posts, friendships, friend requests, groups, memberships, and image services.

### Running a specific test module

For example:

```bash
python -m pytest tests/test_post.py -v
```

You can also run a particular test directory:

```bash
python -m pytest tests/auth_tests -v
```

## Code Quality

The project includes [Ruff](https://docs.astral.sh/ruff/) as a development dependency.

Run Ruff with:

```bash
ruff check .
```

If Ruff reports automatically fixable issues, you can use:

```bash
ruff check . --fix
```

Review automatically applied changes before committing them.

## Development Workflow

The `development` branch is used as the shared integration branch for the project.

A typical development workflow is:

```text
development
    │
    ├── feature/<feature-name>
    │
    └── bugfix/<bug-name>
             │
             ▼
        Pull Request
             │
             ▼
        development
```

### 1. Update your local development branch

```bash
git checkout development
git pull origin development
```

### 2. Create a feature branch

```bash
git checkout -b feature/<feature-name>
```

For example:

```bash
git checkout -b feature/add-comments
```

### 3. Implement the change

Make the required changes and add or update tests where appropriate.

### 4. Run the checks locally

At minimum:

```bash
python -m pytest -v
```

and:

```bash
ruff check .
```

### 5. Commit your changes

Use a clear commit message describing the change:

```bash
git add .
git commit -m "Add comment endpoints"
```

### 6. Push the feature branch

```bash
git push -u origin feature/<feature-name>
```

### 7. Open a Pull Request

Create a Pull Request targeting:

```text
development
```

The changes can then be reviewed before being merged into the shared development branch.

## Continuous Integration

The repository contains a GitHub Actions workflow under:

```text
.github/workflows/tests.yaml
```

The workflow is used to automate project testing through GitHub Actions.

Running the test suite locally before creating a Pull Request helps identify issues before they reach the CI pipeline.

## Development Notes

This project is developed as part of a FastAPI training course and is intended to provide practical experience with building a modular REST API.

The codebase demonstrates several common backend development concepts:

- REST API design
- Dependency injection through FastAPI
- Request/response validation
- ORM-based database access
- Authentication and authorization
- Password hashing
- JWT authentication
- File and image handling
- Automated testing
- Separation of application responsibilities
- Feature-based API routing
- Continuous integration

The project may evolve as new features are implemented, so the automatically generated API documentation at `/docs` should be used for the current API contract.

## Contributing

Contributions should be made through feature or bug-fix branches rather than directly on `development`.

Before opening a Pull Request:

1. Update your branch with the latest `development` changes.
2. Implement the required changes.
3. Add or update tests where applicable.
4. Run the test suite locally.
5. Run the project's code-quality checks.
6. Push your branch.
7. Open a Pull Request targeting `development`.

Keep changes focused on a single feature or issue where possible.

### Branch Naming

When creating a new branch, use one of the following prefixes to specify the purpose of the changes:

- `feature/`   → new functionality
- `fix/`       → fixing an existing issue
- `hotfix/`    → urgent production fix
- `docs/`      → documentation changes
- `chore/`     → maintenance tasks that are not related to a feature or bug fix
- `refactor/`  → code restructuring without changing behavior
- `test/`      → adding or modifying tests

For example:

feature/add-comments  
fix/user-registration-error  
hotfix/fix-production-authentication  
docs/update-installation-guide  
chore/update-dependencies  
refactor/authentication-service  
test/add-group-tests  
