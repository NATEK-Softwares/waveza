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