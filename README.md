# Badge Scanner API

## Intro

Take home assignment for Hack The North 2025 Org Team (Back-end).
https://gist.github.com/SuperZooper3/13ef0b54008e0336f25ee75008fa6812

## Setup

**Dependencies**

```bash
pip install -r requirements.txt
```

**Database** | Also loads the database with the sample json data.

```bash
python helper.py
```

**Run**

```bash
python app.py
```

**Test**

```bash
pytest test.py
```

## Overview

This API is used to scan badges and record the activity.

### Basics

- The database is using SQLite for this assignment.
- The sample json data is loaded into the database using the `helper.py` file.
- The API is using the `app.py` file.
- The tests are using the `test.py` file.

### Tech Stack

- Flask-RESTful for the API endpoints
- Flask-SQLAlchemy for the database ORM
- Pytest for the tests

### Notes

- This is the quick and dirty implementation of the API.
- The database schema should allow for flexibility but lacks the ability to make migrations at this point.
- Some of the design choices were made to be pragmatic for the sake of time and are not the best representations of what I would do for a real project.
  - Having scan count in ActivityModel's fields.
  - Not using a proper logging system.
  - No CI/CD setup.
  - Having all the endpoints in the same file.
  - Subpar input validation.
- It looks like I spent a lot of time on the project but I was on and off of trains for most of it, hence the sporadic commits :).

## API

### Users

- `GET /users` | Get all users with their scan history.
- `GET /users/:id` | Get a user by id with their scan history.
  - id: The id of the user.
- `PUT /users/:id` | Update a user by id.
  - id: The id of the user.
  - Request body (any combination of the following):
    - `name` | The name of the user.
    - `email` | The email of the user.
    - `phone` | The phone number of the user.
    - `badge_code` | The badge code of the user.

### Scan

- `PUT /scan/:id` | Scan a badge and record the activity.
  - id: The id of the user.
  - Request body (all fields are required):
    - `activity_name` | The name of the activity.
    - `activity_category` | The category of the activity.

### Scans

- `GET /scans` | Get all scans with their user and activity history.
  - Query Params:
    - `min_frequency` | The minimum frequency of the scans.
    - `max_frequency` | The maximum frequency of the scans.
    - `activity_category` | The category of the activity.
