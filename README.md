# TaskFlow

TaskFlow is a simple task management backend built with Python and Django.
It allows users to organize their workspaces, boards, columns, and tasks.

## Features

- Create and retrieve workspaces.
- Create and retrieve boards.
- Retrieve boards belonging to a specific workspace.
- Create and retrieve columns.
- Retrieve columns belonging to a specific board.
- Organize columns by position.
- Create and retrieve tasks.
- Retrieve tasks belonging to a specific column.
- Filter tasks by priority and completion status.
- Validate request data and handle errors.

## Technologies

- Python
- Django
- SQLite
- Postman
- Git and GitHub

## Project Structure

```text
taskflow/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── tasks/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── ...
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md