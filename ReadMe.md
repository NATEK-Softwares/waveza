# MishWrites

MishWrites is a Flask-based web application for managing and sharing poetry. The project provides a simple interface for users to create, view, and manage poems.

## Features

- User authentication (register, login, logout)
- Create, edit, and delete poems
- View poems by all users
- Responsive web interface

## Installation

1. **Clone the repository:**
  ```bash
  git clone <repository-url>
  cd MishWrites
  ```

2. **Create a virtual environment:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

3. **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

4. **Set environment variables:**
  ```bash
  export FLASK_APP=app.py
  export FLASK_ENV=development
  ```

5. **Initialize the database:**
  ```bash
  flask db init
  flask db migrate
  flask db upgrade
  ```

6. **Run the application:**
  ```bash
  flask run
  ```

## Project Structure

```
MishWrites/
├── app.py
├── models.py
├── forms.py
├── templates/
├── static/
├── requirements.txt
└── README.md
```

## Usage

- Register for an account or log in.
- Create new poems or browse existing ones.
- Edit or delete your own poems.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.


***COMING SOON***

### Coming Soon

- Reader profile registration and personalized dashboards
- Comment replies for interactive discussions
- Emoji reactions on poems and comments
- Chat forums for community engagement and sharing feedback
- Enhanced poem discovery and search features
- Improved mobile experience and accessibility enhancements
- A compiled mobile application for Android and iOS


**DATE: Sept, 29, 2025 - 23h17**

Perfect 🚀

Here’s a **polished, production-ready README** for your app with **tech stack, frontend, backend, database schema, and UX flow** all included.

---

# MishWrites ✍️

*A Poetry Publishing & Social Platform*

MishWrites is a full-stack web application that allows users to **write, publish, and share poems** while engaging with the community through **likes and comments**. Built with Flask and PostgreSQL, it offers a smooth, modern user experience backed by a clean architecture.

---

## 📌 Project Structure

```
MishWrites/
│── app.py                # Flask entry point
│── models.py             # SQLAlchemy ORM models
│── forms.py              # Flask-WTF forms
│── routes.py             # Application routes
│── templates/            # HTML templates (Jinja2)
│── static/               # CSS, JS, images
│── migrations/           # Database migrations (Flask-Migrate)
│── requirements.txt      # Python dependencies
│── .env                  # Environment variables
│── README.md             # Documentation
```

---

## ⚙️ Tech Stack

**Frontend**

* **HTML5 / Jinja2** → Dynamic templating with Flask
* **CSS3 + Bootstrap 5** → Responsive, mobile-first design
* **JavaScript (Vanilla + Fetch API)** → Interactive actions (likes, comments, live updates)

**Backend**

* **Python 3.10+ (Flask)** → Core web framework
* **Flask-Login** → User authentication & session management
* **Flask-Migrate (Alembic)** → Database schema migrations
* **Passlib (bcrypt)** → Secure password hashing

**Database**

* **PostgreSQL** → Relational database for scalable data storage
* **SQLAlchemy ORM** → Object-relational mapping

**Hosting / Deployment**

* Designed for **Render / Railway / Heroku** deployment
* `.env` configuration for secrets & DB connections

---

## 🗄 Database Schema (ERD)

```mermaid
erDiagram
    USER ||--o{ POEM : writes
    USER ||--o{ COMMENT : makes
    USER ||--o{ LIKE : gives
    POEM ||--o{ COMMENT : has
    POEM ||--o{ LIKE : receives

    USER {
        int id PK
        string username
        string email
        string password
        datetime created_at
    }

    POEM {
        int id PK
        int user_id FK
        string title
        string slug
        text content
        string category
        string thumbnail
        datetime created_at
    }

    COMMENT {
        int id PK
        int user_id FK
        int poem_id FK
        text content
        datetime created_at
    }

    LIKE {
        int id PK
        int user_id FK
        int poem_id FK
        datetime created_at
    }
```

---

## 🔄 User Experience Flow

```mermaid
flowchart TD
    A[Landing Page / Home] --> B[Register]
    A --> C[Login]

    B -->|POST /register| D[Dashboard]
    C -->|POST /login| D

    D --> E[Add Poem]
    D --> F[View Own Poems]
    D --> G[Profile / Stats]

    E -->|POST /add_poem| H[Poem Detail Page]
    F --> H
    A --> H

    H --> I[Like Poem]
    H --> J[Comment on Poem]

    I --> H
    J --> H

    G --> D
    H --> D
```

---

## 🎨 UX / UI Specs

* **Landing Page**

  * Displays latest poems & featured works
  * Categories filter for navigation

* **Registration / Login**

  * Simple forms with input validation
  * Secure password hashing via bcrypt (Passlib)

* **Dashboard**

  * Overview of user activity (poems, likes, comments)
  * Quick actions: *Add poem, View poems*

* **Poem Page**

  * Rich text poem display with category and metadata
  * Interactive like & comment section

* **Profile Page**

  * Personal stats (total poems, engagement received)
  * Edit profile option (future enhancement)

---

## 🚀 Setup & Run

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/MishWrites.git
   cd MishWrites
   ```

2. **Create virtual environment & install deps**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

3. **Configure `.env`**

   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/poetrydb
   SECRET_KEY=your_secret_key
   FLASK_ENV=development
   ```

4. **Initialize database**

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Run the app**

   ```bash
   flask run
   ```

---

## ✅ Roadmap / Future Enhancements

* [ ] User profiles with avatars & bio
* [ ] Search & tagging system for poems
* [ ] Email verification & password reset
* [ ] Admin dashboard for moderation
* [ ] Progressive Web App (PWA) support


🎁 
### Engagement & Exclusive Content Features

***To incentivize participation and create a sense of ownership:***

### Featured Poems 
  → Highlight top user-submitted poems on the front page

### Badges & Achievements 
  → Earn badges for submissions, comments, and engagement

### User Profiles 
  → Showcase user’s work, bio, and favorite poems

### Community Challenges 
  → Participate in themed writing challenges

### Curated Collections 
  → Users can create & share collections of poems

### Recognition for Contributors 
  → Top contributors & most popular poets are highlighted

### Exclusive Content 
  → Behind-the-scenes stories or insights for active users
---

📖 With this README, any developer can **understand, set up, and extend MishWrites** confidently.

---
