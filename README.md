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

## Usage

Once the application is running, navigate to `http://127.0.0.1:5000/` in your web browser to access the application. Here are the primary routes available:

- `/`: The home page that serves as the entry point to the application.
- `/add_edit_delete`: Interface for adding, editing, and deleting meetings.
- `/manage_organizers`: Manage which students can organize meetings.
- `/invites_rsvps`: Send out invitations to meetings and manage RSVPs.
- `/report`: Generate and view reports based on various filtering criteria such as date, club, and room.

### Indexing Strategy

To optimize the performance of the database queries, especially those that are frequently accessed or require high efficiency, indexes have been established on critical tables:

- **Meetings Table**: Indexed on `(date, club_id, room_id)` to facilitate fast retrieval of meetings based on specific criteria which is crucial for generating reports and managing meeting schedules efficiently.
- **RSVPs Table**: Indexed on `(meeting_id, student_id)` to quickly access and manage RSVPs, improving responsiveness when updating or querying RSVP statuses.

These indexes are critical in ensuring that the application performs efficiently even as the amount of data grows.

Hello
