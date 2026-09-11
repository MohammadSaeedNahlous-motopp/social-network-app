# Social Network Application API

A RESTful backend API for a modern social networking application, built with **FastAPI**.

The application provides the core functionality required for a social networking platform, allowing users to connect with each other, manage friendships, participate in groups, share content, control privacy, and interact through a growing set of social features.

The project focuses not only on functionality, but also on **automated testing, security, professional Git workflows, collaboration, and maintainable backend architecture**.

---

## 🚀 Features

### 🔐 Authentication

- User registration
- User login
- JWT-based authentication
- Protected API endpoints
- Secure authentication using an environment-based secret key

> 🔜 **Planned:** Refresh token authentication.

### 👤 User Management

- View user profiles
- Search and browse users
- Edit user profiles
- Upload profile images
- Change profile images
- Remove profile images

### 🤝 Friends & Friend Requests

- Send friend requests
- Accept friend requests
- Decline friend requests
- Cancel friend requests
- View pending and sent friend requests
- View a user's friends list

### 👥 Groups

- Create groups
- Update groups
- Delete groups
- View group details
- Search and browse groups
- Join groups
- Leave groups
- Manage group members
- Role-based permissions
- Public and private groups

### 📝 Posts

- Create posts
- Edit posts
- Delete posts
- View posts and feeds
- Create and view group posts
- Post privacy rules

### 🖼️ Secure Image Uploads

The application supports image uploads for:

- User profile images
- Post images
- Group images

Uploaded images are protected through multiple validation layers:

- Allowed content type validation
- File size validation
- Image integrity verification using **Pillow**
- Unique filename generation using UUIDs

**Supported formats:**

- JPG / JPEG
- PNG
- WEBP

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.14 | Programming language |
| FastAPI | Backend web framework |
| SQLAlchemy | Database ORM |
| SQLite | Local development database |
| Uvicorn | ASGI server |
| Pytest | Automated testing |
| Pillow | Image validation |
| JWT | Authentication |
| GitHub Actions | Continuous Integration |
| Ruff | Code formatting |
| Git & GitHub | Version control and collaboration |

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone <repository-url>
```

### 2. Navigate to the project directory

```bash
cd social-network-app
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

#### Windows

```bash
.venv\Scripts\activate
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the project root:

```env
AUTH_SECRET_KEY=your_secret_key_here
```

> ⚠️ Never commit your real secret key to the repository.

The `AUTH_SECRET_KEY` is used by the authentication system for JWT token generation and validation.

---

## 🗄️ Database

The application currently uses **SQLite** for local development.

The database file is:

```text
social-network.db
```

The application automatically creates the database in the project root directory if it does not already exist.

No manual database creation is required for local development.

---

## ▶️ Running the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The application will typically be available at:

```text
http://127.0.0.1:8000
```

The `--reload` option automatically restarts the server when changes are made during development.

---

## 📚 API Documentation

FastAPI provides interactive API documentation.

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

The documentation allows developers to:

- Explore available API endpoints
- View request and response models
- Test endpoints directly from the browser
- Test authenticated endpoints

---

## 🧪 Automated Testing

The project currently contains approximately **140 automated tests**.

Testing is implemented using **Pytest**, with a dedicated testing environment and FastAPI testing tools.

### Run all tests

```bash
pytest -v
```

### Run tests with coverage

```bash
pytest --cov
```

The automated test suite helps verify functionality and detect regressions as the application continues to grow.

---

## 🎨 Code Formatting

The project uses **Ruff** for code formatting.

Format the codebase with:

```bash
ruff format .
```

---

## 🔄 Continuous Integration

The project uses **GitHub Actions** for Continuous Integration.

The CI pipeline automatically runs the **Pytest test suite on Pull Requests**, helping detect regressions before changes are merged.

The workflow helps ensure that:

- Changes are automatically tested
- Regressions can be detected early
- Pull Requests are validated before merging

---

## 🌿 Git Workflow

The project follows a **feature-branch-based development workflow**.

Developers work on dedicated feature branches and submit changes through Pull Requests rather than directly modifying important branches.

Examples of feature branches include:

```text
feature/authentication
feature/automated_testing
feature/friend-requests
feature/group_implementation
feature/post
```

### Branch Protection

Important branches are protected to maintain code quality and stability.

The workflow includes:

- ❌ No direct pushes to `main`
- ❌ No direct pushes to the development branch
- ✅ All changes go through Pull Requests
- ✅ Pull Requests require **2 reviews**
- ✅ All review conversations must be resolved before merging

This ensures that changes are reviewed and discussed before becoming part of the protected codebase.

---

## 🏗️ Architecture

The application follows a modular backend architecture to separate responsibilities and improve maintainability.

The project is organized around different areas of responsibility, including:

- Authentication
- Database models
- API routers
- Application schemas
- Business logic
- Testing
- File uploads

This approach makes the application easier to maintain and extend as additional social networking features are introduced.

---

## 🔒 Security

Security considerations are integrated into several parts of the application.

Current security-related functionality includes:

- JWT-based authentication
- Protected API endpoints
- Environment-based authentication secrets
- Post privacy rules
- Public and private groups
- Role-based group permissions
- Secure image upload validation
- File size restrictions
- Content type validation
- Image verification using Pillow

---

## 🗺️ Roadmap

The application is actively being developed and will continue to grow.

### 🔐 Advanced Authentication

- Refresh token authentication
- Improved token management

### 💬 Chat System

- Direct messaging between users
- Messaging functionality

### 🔔 Notification System

- Friend request notifications
- Social interaction notifications
- Application activity notifications

### 💬 Comments

- Add comments to posts
- Manage discussions and interactions

### ❤️ Reactions

- React to posts
- Improve social interaction

### ✨ Quality of Life Improvements

- API improvements
- Additional privacy controls
- General application improvements

---

## 🎯 Project Goals

This project is not intended to be a one-time assignment that is abandoned after completion.

The goal is to continue developing the application into a substantial and professional portfolio project.

The team aims to:

- Continue adding advanced features
- Improve security and authentication
- Expand social interaction features
- Maintain strong automated testing
- Follow professional Git workflows
- Improve code quality and maintainability

The project is intended to become part of the developers' **professional portfolios and CVs**.

---

## 🤝 Development Philosophy

The project focuses on more than simply implementing features.

Important development principles include:

- Automated testing
- Regression prevention
- Code reviews
- Protected branches
- Pull Request workflows
- Modular architecture
- Security considerations
- Maintainable code
- Continuous improvement

The goal is to build the application using practices that reflect a professional software development environment.

---

## 📈 Project Status

🚧 **Actively under development**

The application already includes a substantial foundation of social networking functionality, including:

- Authentication
- User management
- Friendships and friend requests
- Groups and role management
- Posts and privacy rules
- Group posts
- Secure image uploads
- Approximately 140 automated tests
- GitHub Actions Continuous Integration
- Protected branches and Pull Request reviews

Future development will focus on **refresh tokens, messaging, notifications, comments, reactions, and additional quality-of-life improvements**.

---

## 👨‍💻 Contributors

This project is developed collaboratively by a team of developers.

Contributors and GitHub profiles can be added here.

---

## 📄 License

This project currently does not have a license specified.

---

## ⭐ Final Note

**Social Network Application API** is an actively evolving backend project designed to explore modern backend development while building a functional social networking platform.

The project combines practical backend development with professional engineering practices such as **automated testing, Continuous Integration, protected branches, code reviews, secure file handling, and collaborative development**.
