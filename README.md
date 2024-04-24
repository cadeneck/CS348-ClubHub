# CS348 Database-Backed Web Application

This project is a Flask-based web application developed for the CS348 course. It manages student clubs, meetings, and RSVPs, supporting a database-backed system with a focus on efficient data handling through proper indexing and database management practices.

## Features

- **User Management**: Allows adding, editing, and deleting student profiles.
- **Club Management**: Manage details about student clubs including club creation and description updates.
- **Meeting Management**: Users can create, update, or delete meetings for clubs in specific rooms and times.
- **RSVP Management**: Manage RSVPs for meetings, allowing students to respond to invitations.
- **Report Generation**: Generate reports based on meetings filtered by date, club, and room, including statistics like average attendance and duration.

## Technologies Used

- **Flask**: A micro web framework written in Python.
- **SQLAlchemy**: SQL toolkit and ORM for Python.
- **SQLite**: Database engine used for development.
- **HTML/CSS**: For the frontend user interface.

## Installation

To set up the project on your local machine, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/cs348-project.git
   cd cs348-project
