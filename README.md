# Course Website

## Description
This project is a web application for managing a university course. It is built using Flask, a lightweight WSGI web application framework in Python. The application allows users to register, login, view course materials, submit assignments, and view grades.

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [Technologies Used](#techonologies-used)
- [Acknowledgements](#acknowledgements)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/muxunzzz/course-website
   cd course-website
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```
5. Run the application:
   ```bash
   flask run
   ```
6. Open your web browser and navigate to `http://127.0.0.1:5000`

## Dependencies
- **Flask**: Web application framework for Python providing routing, middleware, and HTTP utilities.
- **Flask-SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library for Flask applications.
- **Flask-Bcrypt**: Extension for Flask that provides bcrypt hashing utilities for password hashing.
- **Jinja2**: Template engine for Python to generate dynamic HTML pages.
- **SQLite**: Lightweight, disk-based database that doesn't require a separate server process.

## Techonologies Used

Frontend
- **HTML**: Markup language for structuring web pages.
- **CSS**: Stylesheet language for designing and enhancing HTML elements.
- **Jinja2**: Template engine for generating dynamic HTML content.

Backend
- **Flask**: Web framework for building web applications with Python.
- **SQLAlchemy**: SQL toolkit and ORM for managing database operations.
- **SQLite**: Relational database management system for storing and managing data.

## Acknowledgements
- This is a coursework for CSCB20H3.
- Contributors: [@Muxun Zhang](https://github.com/muxunzzz)