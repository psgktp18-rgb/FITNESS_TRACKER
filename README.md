# HEALTHYFY TRACKER

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.13 |
| **Backend Framework** | Django 5, Django REST Framework |
| **Frontend** | Bootstrap 5, HTMX, CSS3 Variables |
| **Database** | SQLite (Development) / PostgreSQL (Production) |
| **Icons & Fonts** | FontAwesome 6, Google Fonts (Poppins, Inter, Bebas Neue) |
| **Package Manager** | `uv` (recommended) or `pip` |

---

## 🚀 Getting Started

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/wger-master.git
cd wger-master
```

> Replace `your-username` with the actual GitHub username or org where the repo is hosted.

---

### Step 2 — Install Dependencies

**Option A — Using `uv` (recommended):**

```bash
uv sync
```

**Option B — Using `pip` with a virtual environment:**

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install the project
pip install -e .
```

---

### Step 3 — Apply Database Migrations

```bash
uv run python manage.py migrate --settings=settings.local_dev
```

> If using `pip`, replace `uv run` with just `python` (make sure your venv is activated).

---

### Step 4 — Populate Default Test Users

```bash
uv run python manage.py setup_default_users --settings=settings.local_dev
```

This seeds the database with sample accounts covering all user roles (admin, trainer, members).

---

### Step 5 — Start the Development Server

```bash
uv run python manage.py runserver --settings=settings.local_dev 127.0.0.1:8000
```

---

### Step 6 — Open in Browser

Navigate to:

```
http://127.0.0.1:8000/
```

Or go directly to the features landing page:

```
http://127.0.0.1:8000/en/software/features
```

---

## 🔑 Pre-Configured Test Accounts

| Username | Password | Role |
| :--- | :--- | :--- |
| `admin` | `Admin@12345` | System Administrator |
| `demo` | `Demo@12345` | Active Member |
| `trainer_alex` | `Trainer@12345` | Personal Trainer |
| `fitness_sarah` | `Sarah@12345` | Athlete / Member |
| `mike_runner` | `Mike@12345` | Athlete / Member |

---

