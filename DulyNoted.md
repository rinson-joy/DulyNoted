# DulyNoted.md

## Project Overview

**DulyNoted** is a secure, web-based note-taking application built with Python and Flask. It provides a lightweight platform for users to create, manage, share, and export their notes. The project follows a modular architecture using Flask Blueprints and utilizes MongoDB for data persistence.

### Main Technologies
- **Backend:** [Flask](https://flask.palletsprojects.com/) (Python 3.x)
- **Database:** [MongoDB](https://www.mongodb.com/) via `pymongo`
- **Frontend:** [Jinja2](https://jinja.palletsprojects.com/) templates and custom CSS
- **Authentication:** Custom session-based authentication with role-based access control (RBAC).

### Architecture
- `server/`: Contains the core application logic.
    - `main.py`: Entry point for the application. Handles configuration and Blueprint registration.
    - `monkey.py`: Database connection setup and common decorators (`@login_required`, `@admin_required`).
    - `routes/`: Modular route definitions.
        - `login.py`: User authentication (login, registration, logout).
        - `notes.py`: Core note CRUD operations, including import/export logic.
        - `share.py`: Note sharing functionality.
        - `admin.py`: Administrative routes (requires "master" role).
- `templates/`: Jinja2 HTML templates for all pages.
- `beaut/`: Static directory containing CSS (`ooo.css`) and other UI assets.

---

## Building and Running

### Prerequisites
- Python 3.x
- MongoDB instance (Local or Atlas)
- Required Python packages: `flask`, `pymongo`, `bson`

### Environment Variables
The application relies on two critical environment variables:
- `apple`: Execution mode.
    - Set to `'apple keeps doc away'` for **Development Mode** (enables debug).
    - Any other value triggers **Production Mode** (binds to `0.0.0.0:5000` with SSL context).
- `banana`: MongoDB connection string (e.g., `mongodb+srv://user:pass@cluster.mongodb.net/`).

### Running Locally (PowerShell)
```powershell
$env:apple = 'apple keeps doc away'
$env:banana = 'your_mongodb_connection_string'
python server/main.py
```

### Deployment
A `deploy.sh` script is available for production updates. It pulls from the `main` branch and restarts the `dulynoted` systemd service.

---

## Development Conventions

### Routing & Logic
- **Modular Routes:** All new functionality should be implemented as a Flask Blueprint in `server/routes/`.
- **API Responses:** Use `flask.jsonify` for all JSON API endpoints to ensure consistent response formatting.
- **Database Access:** Use the pre-configured collections (`userdata`, `notes_col`, `share_col`) from `server/monkey.py`.

### Security & Access Control
- **Route Protection:** Use the `@login_required` decorator from `monkey.py` for any route requiring an authenticated user.
- **Admin Features:** Use the `@admin_required` decorator for routes reserved for the "master" role. Note that "master" accounts cannot be created via the UI.
- **Data Integrity:** Always validate that the current user owns the resource (e.g., a note) before performing `UPDATE` or `DELETE` operations.

### Styling & UI
- **CSS:** All styles are centralized in `beaut/ooo.css`. Avoid inline styles.
- **Templates:** Use the Jinja2 template inheritance pattern (extending `base.html`) for consistency across pages.

---

## Roadmap & Notes
- **Future Migration:** A migration to React for the frontend is planned.
- **Data Portability:** Supports exporting notes in JSON and TXT formats and importing from the same.
