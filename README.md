# ⚡ FastAPI Blog & Social Application

A full-stack, asynchronous blog and social publishing platform built with **FastAPI**, **SQLAlchemy 2.0 (Async)**, **SQLite (aiosqlite)**, and **Jinja2 Templates**. 

This project demonstrates a hybrid architecture: providing both **server-rendered web pages** for visitors and a full-featured, type-safe **REST API** for modern client consumption.

---

## ✨ Features

- **🚀 Modern Asynchronous Stack**: Powered by `asyncio`, `AsyncSession`, and `sqlite+aiosqlite` for non-blocking I/O.
- **⚡ SQLAlchemy 2.0 ORM**: Type-annotated models with `Mapped`, `mapped_column`, and automatic async relationship loading via `lazy="selectin"`.
- **🌐 Server-Rendered Web Pages**: Clean HTML views built with Jinja2 template inheritance, custom date formatting, and responsive styling.
- **🛡️ Robust Type Validation**: Request and response schema validation using Pydantic v2.
- **🔄 Hybrid Exception Handling**:
  - Automatically returns structured **JSON** errors for `/api/*` endpoints.
  - Automatically renders a friendly **HTML error page** (`error.html`) for browser requests.
- **🌱 Data Seeding**: Built-in script (`seed.py`) to quickly populate realistic sample users and blog posts.
- **📁 Static & Media Storage**: Support for profile pictures and media assets mounted via `StaticFiles`.
- **📖 Auto-Generated Documentation**: Interactive Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## 🏗️ Project Architecture

```
FastAPI/
├── database.py       # Async engine, AsyncSessionLocal, and get_db dependency
├── main.py           # FastAPI app, lifespan manager, routes & exception handlers
├── models.py         # SQLAlchemy ORM models (User, Post)
├── schemas.py        # Pydantic schemas (UserCreate, PostResponse, etc.)
├── seed.py           # Database seeder script for sample data
├── posts.db          # Local SQLite database (git-ignored)
├── static/           # Static CSS, JS, and default profile assets
├── media/            # User-uploaded files and media
└── templates/        # Jinja2 HTML templates
    ├── layout.html       # Base layout with navbar and footer
    ├── home.html         # Post feed
    ├── post.html         # Single post detail view
    ├── user_posts.html   # Author-specific post listing
    └── error.html        # Custom error page
```

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have Python **>= 3.12** and [uv](https://github.com/astral-sh/uv) installed.

### 2. Clone and Setup
```bash
git clone <your-repo-url>
cd FastAPI
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. (Optional) Seed the Database
Populate the database with sample users and articles:
```bash
uv run python seed.py
```

### 5. Run the Development Server
```bash
uv run fastapi dev main.py
```
The server will start at **http://127.0.0.1:8000** with auto-reload enabled.

---

## 🌐 Web Routes (Browser)

| Route | Method | Description |
|---|---|---|
| `/` or `/posts` | `GET` | Home feed listing all blog posts |
| `/posts/{post_id}` | `GET` | View a single post and its content |
| `/users/{user_id}/posts` | `GET` | View all posts authored by a specific user |

---

## 📡 REST API Reference

All API routes are served under `/api` and return JSON.

### User Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/user` | Create a new user account |
| `GET` | `/api/users/{user_id}` | Retrieve user profile by ID |
| `PUT` | `/api/users/{user_id}` | Full update of user information |
| `PATCH` | `/api/users/{user_id}` | Partial update of user details |
| `DELETE` | `/api/users/{user_id}` | Delete user account (HTTP 204) |
| `GET` | `/api/user/{user_id}/posts` | Fetch all posts by a specific user |

### Post Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/posts` | List all posts (with author details) |
| `POST` | `/api/posts` | Create a new post |
| `GET` | `/api/posts/{post_id}` | Get post details by ID |
| `PUT` | `/api/posts/{post_id}` | Full update of a post |
| `PATCH` | `/api/posts/{post_id}` | Partial update of a post |
| `DELETE` | `/api/posts/{post_id}` | Delete a post (HTTP 204) |

---

## 📚 Interactive API Documentation

When the application is running, visit:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
