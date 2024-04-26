from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy import case
from datetime import datetime
from flask import flash
from sqlalchemy import event
import enum
from sqlalchemy import DDL
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine



# Create a Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cs348.db'
app.config['SECRET_KEY'] = 'secret-key'
db = SQLAlchemy(app)

# Enum for RSVP status
class RSVPStatus(enum.Enum):
    yes = "yes"
    no = "no"
    maybe = "maybe"

# Students table to store student details
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

# Clubs table to store club details
class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    description = db.Column(db.String(500))

# Rooms table to store room details
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(100))
    number = db.Column(db.String(50))
    max_capacity = db.Column(db.Integer)

# Meetings table to store meeting details
class Meetings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer)
    description = db.Column(db.String(500))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    club = db.relationship('Club', backref=db.backref('meetings', lazy=True))
    room = db.relationship('Room', backref=db.backref('meetings', lazy=True))

# Many-to-Many relationship table for meeting organizers
class MeetingOrganizers(db.Model):
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    meeting = db.relationship('Meetings', backref=db.backref('organizers', lazy=True))
    student = db.relationship('Student', backref=db.backref('organized_meetings', lazy=True))

# RSVPs table to store student responses to meeting invitations
class RSVPs(db.Model):
    rsvp_id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    status = db.Column(db.Enum(RSVPStatus))
    meeting = db.relationship('Meetings', backref=db.backref('rsvps', lazy=True))
    student = db.relationship('Student', backref=db.backref('rsvps', lazy=True))

def initialize_database():
    # Check if the database already has entries to prevent re-initialization
    if not Student.query.first():
        # No students found, assuming database is empty and needs initialization
        
        # Create Clubs
        club_list = [
            Club(name="Chess Club", address="123 Checkmate Lane", description="A club for chess enthusiasts."),
            Club(name="Coding Club", address="456 Code St", description="Learn to code in various languages."),
            Club(name="Literature Club", address="789 Novel Ave", description="Discussing classic and contemporary literature.")
        ]

        # Create Rooms
        room_list = [
            Room(building="A", number="101", max_capacity=30),
            Room(building="B", number="202", max_capacity=20),
            Room(building="C", number="303", max_capacity=25)
        ]

        # Create Students
        student_list = [
            Student(name="John Doe", email="john.doe@example.com"),
            Student(name="Jane Smith", email="jane.smith@example.com"),
            Student(name="Alice Johnson", email="alice.johnson@example.com")
        ]

        # Add and commit Clubs, Rooms, and Students to the database
        db.session.add_all(club_list + room_list + student_list)
        db.session.commit()

        db.engine.execute(DDL("CREATE INDEX IF NOT EXISTS idx_meetings_date_club_room ON Meetings(date, club_id, room_id);"))
        db.engine.execute(DDL("CREATE INDEX IF NOT EXISTS idx_rsvps_meeting_student ON RSVPs(meeting_id, student_id);"))

        print("Database initialized with clubs, rooms, and students.")
    else:
        print("Database already initialized. Skipping.")


# Define routes for the application
@app.route('/')
def home():
    return render_template('home.html')


# Route to add, edit, or delete meetings
@app.route('/add_edit_delete', methods=['GET', 'POST'])
def add_edit_delete():
    if request.method == 'POST':
        action = request.form.get('action')
        print(action)
        
        if action == "delete":
            # Handle delete action
            meeting_id = request.form.get('meetingID')
            meeting = Meetings.query.get(meeting_id)
            if meeting:

                try:
                    db.session.delete(meeting)
                    db.session.commit()
                    flash('Meeting deleted successfully!', 'success')
                    print('Meeting deleted successfully!')
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to deleted. Error: ' + str(e), 'error')
                    print('Failed to deleted. Error: ' + str(e))
                
            else:
                flash('Meeting not found.', 'error')
                print('Meeting not found1.')
        else:
            meeting_id = request.form.get('meetingID')

            # Extract form data common to both adding and editing actions
            meeting_date_str = request.form.get('meetingDate')
            meeting_time_str = request.form.get('meetingTime')
            meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d').date() if meeting_date_str else None
            meeting_time = datetime.strptime(meeting_time_str, '%H:%M').time() if meeting_time_str else None
            duration = request.form.get('duration')
            description = request.form.get('description')
            club_id = request.form.get('club_id')
            room_id = request.form.get('room_id')
            print('Data:' + meeting_id, meeting_date, meeting_time, duration, description, club_id, room_id)
            
            if meeting_id:
                # Edit existing meeting
                meeting = Meetings.query.get(meeting_id)
                print('Meeting:', meeting)
                if meeting:
                    # Update meeting with new details from the form
                    meeting.date = meeting_date
                    meeting.time = meeting_time
                    meeting.duration = duration
                    meeting.description = description
                    meeting.club_id = club_id
                    meeting.room_id = room_id

                    try:
                        db.session.commit()
                        flash('Meeting updated successfully!', 'success')
                        print('Meeting updated successfully!')
                    except Exception as e:
                        db.session.rollback()
                        flash('Failed to update. Error: ' + str(e), 'error')
                        print('Failed to update. Error: ' + str(e))
                else:
                    # Meeting not found, create a new meeting instead
                    new_meeting = Meetings(
                        id=meeting_id,
                        date=meeting_date,
                        time=meeting_time,
                        duration=duration,
                        description=description,
                        club_id=club_id,
                        room_id=room_id
                    )

                    try:
                        db.session.add(new_meeting)
                        db.session.commit()
                        flash('Meeting added successfully!', 'success')
                        print('Meeting added successfully!')
                    except Exception as e:
                        db.session.rollback()
                        flash('Failed to add. Error: ' + str(e), 'error')
                        print('Failed to add. Error: ' + str(e))
                    

                    
            
        #return redirect(url_for('add_edit_delete'))

    # GET request logic remains the same for fetching clubs and rooms
    clubs = Club.query.all()
    rooms = Room.query.all()
    return render_template('add_edit_delete.html', clubs=clubs, rooms=rooms)


"""
@app.route('/manage_organizers', methods=['GET', 'POST'])
def manage_organizers():
    if request.method == 'POST':
        action = request.form.get('action')
        meeting_id = request.form.get('meeting_id')
        student_id = request.form.get('student_id')  # Get the student_id from the form

        if action == 'add':
            # Check if the meeting and student exist
            meeting = Meetings.query.get(meeting_id)
            student = Student.query.get(student_id)

            if meeting and student:
                # Check if the organizer already exists for this meeting
                existing_organizer = MeetingOrganizers.query.filter_by(
                    meeting_id=meeting_id, student_id=student_id
                ).first()

                if not existing_organizer:
                    # Create a new MeetingOrganizers entry
                    new_organizer = MeetingOrganizers(
                        meeting_id=meeting_id,
                        student_id=student_id
                    )
                    db.session.add(new_organizer)
                    db.session.commit()
                    flash('Organizer added successfully!', 'success')
                    print('Organizer added successfully!')
                else:
                    flash('This organizer is already added to the meeting.', 'warning')
                    print('This organizer is already added to the meeting.')
            else:
                flash('Meeting or Student not found.', 'error')
                print('Meeting or Student not found.')

        elif action == 'delete':
            student_id = request.form.get('student_id')  # Assuming the form now sends student_id
            if not student_id or not meeting_id:
                flash('Meeting or Organizer not specified.', 'error')
                print('Meeting or Organizer not specified.')
                return redirect(url_for('manage_organizers'))

             # Check directly if an organizer entry exists for this meeting and student
            organizer = MeetingOrganizers.query.filter_by(
                meeting_id=meeting_id, student_id=student_id
            ).first()

            if organizer:
                db.session.delete(organizer)
                db.session.commit()
                flash('Organizer deleted successfully!', 'success')
                print('Organizer deleted successfully!')
            else:
                flash('Organizer not found.', 'error')
                print('Organizer not found.')

        #return redirect(url_for('manage_organizers'))

    meetings = Meetings.query.all()
    # Only fetching meetings and students for add form; organizers are not pre-loaded for delete form
    students = Student.query.all()
    return render_template('manage_organizers.html', meetings=meetings, students=students)
"""

# Route to manage organizers for a meeting
@app.route('/manage_organizers', methods=['GET', 'POST'])
def manage_organizers():
    if request.method == 'POST':
        # Extract form data for adding or deleting organizers
        action = request.form.get('action')
        meeting_id = request.form.get('meeting_id')
        student_id = request.form.get('student_id')

        # Validate meeting and student existence
        meeting_exists = db.session.query(Meetings.query.filter_by(id=meeting_id).exists()).scalar()
        student_exists = db.session.query(Student.query.filter_by(id=student_id).exists()).scalar()

        if not meeting_exists or not student_exists:
            flash('Meeting or Student not found.', 'error')
            print('Meeting or Student not found.')
            return redirect(url_for('manage_organizers'))

        if action == 'add':
            # Prepared statement to check and add an organizer if they don't already exist
            stmt = text(
                """
                INSERT INTO meeting_organizers (meeting_id, student_id)
                SELECT :meeting_id, :student_id
                WHERE NOT EXISTS (
                    SELECT 1 FROM meeting_organizers
                    WHERE meeting_id = :meeting_id AND student_id = :student_id
                )
                """
            )
            
            try:
                db.session.execute(stmt, {'meeting_id': meeting_id, 'student_id': student_id})
                db.session.commit()
                flash('Organizer added successfully!', 'success')
                print('Organizer added successfully!')
            except Exception as e:
                db.session.rollback()
                flash('Failed to delete. Error: ' + str(e), 'error')
                print('Failed to delete. Error: ' + str(e))
            

        elif action == 'delete':
            # Prepared statement for deleting an organizer
            stmt = text(
                "DELETE FROM meeting_organizers WHERE meeting_id = :meeting_id AND student_id = :student_id"
            )
            result = db.session.execute(stmt, {'meeting_id': meeting_id, 'student_id': student_id})
            if result.rowcount > 0:
                try:
                    db.session.commit()
                    flash('Organizer deleted successfully!', 'success')
                    print('Organizer deleted successfully!')
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to delete. Error: ' + str(e), 'error')
                    print('Failed to delete. Error: ' + str(e))
            else:
                flash('Organizer not found.', 'error')
                print('Organizer not found.')

    # Fetch all meetings and students to populate the form dropdowns
    meetings = Meetings.query.all()
    students = Student.query.all()
    return render_template('manage_organizers.html', meetings=meetings, students=students)


# Route to manage RSVPs for meeting invitations
@app.route('/invites_rsvps', methods=['GET', 'POST'])
def invites_rsvps():
    if request.method == 'POST':
        # Extract form data for RSVP actions
        rsvp_id = request.form.get('rsvp_id')
        meeting_id = request.form.get('meeting_id')
        student_id = request.form.get('student_id')
        action = request.form.get('action')
        print('Data:', meeting_id, student_id, action)

        if action == 'Send Invitation':
            rsvp = RSVPs.query.filter_by(meeting_id=meeting_id, student_id=student_id).first()
            if rsvp:
                flash('RSVP already exists for this student.', 'warning')
                print('RSVP already exists for this student.')
                return redirect(url_for('invites_rsvps'))
            else:
                # Create a new RSVP entry with a default status of 'MAYBE'
                new_rsvp = RSVPs(
                    rsvp_id = rsvp_id,
                    meeting_id=meeting_id,
                    student_id=student_id,
                    status=RSVPStatus.maybe  # Assuming RSVPStatus is an Enum
                )

                try:
                    db.session.add(new_rsvp)
                    db.session.commit()
                    flash('Invitation sent successfully!', 'success')
                    print('Invitation sent successfully!')
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to send invitation. Error: ' + str(e), 'error')
                    print('Failed to send invitation. Error: ' + str(e))

        elif action == 'Record Response':
            rsvp_status = request.form.get('rsvp_status').lower()
            # Update the existing RSVP entry with the new status
            rsvp = RSVPs.query.filter_by(meeting_id=meeting_id, student_id=student_id).first()
            if rsvp:
                rsvp.status = RSVPStatus(rsvp_status)
                try:
                    db.session.commit()
                    flash('RSVP response recorded!', 'success')
                    print('RSVP response recorded!')
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to record RSVP response. Error: ' + str(e), 'error')
                    print('Failed to record RSVP response. Error: ' + str(e))
            else:
                flash('RSVP not found.', 'error')
                print('RSVP not found.')

        elif action == 'Delete RSVP':
            # Delete the RSVP entry
            rsvp = RSVPs.query.filter_by(meeting_id=meeting_id, student_id=student_id).first()
            if rsvp:
                
                try:
                    db.session.delete(rsvp)
                    db.session.commit()
                    flash('RSVP deleted successfully!', 'success')
                    print('RSVP deleted successfully!')
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to delete. Error: ' + str(e), 'error')
                    print('Failed to delete. Error: ' + str(e))
                
            else:
                flash('RSVP not found.', 'error')
                print('RSVP not found.')

        else:
            flash('Invalid action.', 'error')
            print('Invalid action.')

    # Prepare data for GET requests or after form submission
    meetings = Meetings.query.all()
    students = Student.query.all()
    # Optionally, include RSVPs to show current invites and responses
    rsvps = RSVPs.query.join(Meetings).join(Student).all()

    return render_template('invites_rsvps.html', meetings=meetings, students=students, rsvps=rsvps)


# Route to input information needed to generate a report
@app.route('/report')
def report():
    # Fetch all clubs and rooms to populate the form's dropdowns
    clubs = Club.query.all()
    rooms = Room.query.all()
    default_reports = None
    return render_template('report.html', clubs=clubs, rooms=rooms)

# Route to generate a report based on meeting data
@app.route('/w', methods=['POST'])
def generate_report():
    # Use .get() to safely access form data, providing a fallback value as needed
    start_date = request.form.get('startDate')
    end_date = request.form.get('endDate')
    club_id = request.form.get('club_id', '')
    room_id = request.form.get('room_id', '')

    # Ensure all required form data is provided
    if not start_date or not end_date or not club_id or not room_id:
        flash("All fields are required.", "error")
        return redirect(url_for('report'))

    # Continue with filtering meetings based on the provided inputs
    filtered_meetings = Meetings.query.filter(
        Meetings.date.between(start_date, end_date),
        Meetings.club_id == club_id,
        Meetings.room_id == room_id
    ).all()

    # Aggregate data for invitedCount and acceptedCount
    RSVPsAlias = aliased(RSVPs)
    accepted_count = func.sum(case((RSVPsAlias.status == RSVPStatus.yes.name, 1), else_=0)).label('acceptedCount')

    meetings_with_counts = db.session.query(
        Meetings.id,
        func.count(RSVPsAlias.rsvp_id).label('invitedCount'),
        accepted_count
    ).join(RSVPsAlias, RSVPsAlias.meeting_id == Meetings.id, isouter=True).filter(
        Meetings.date.between(start_date, end_date),
        Meetings.club_id == club_id,
        Meetings.room_id == room_id
    ).group_by(Meetings.id).all()

    # Calculate the average duration, if needed
    average_duration = db.session.query(func.avg(Meetings.duration)).filter(
        Meetings.date.between(start_date, end_date),
        Meetings.club_id == club_id,
        Meetings.room_id == room_id
    ).scalar()

    # Re-fetch clubs and rooms for form dropdowns to preserve state
    clubs = Club.query.all()
    rooms = Room.query.all()

    # Return the report results, including re-provided dropdown data
    return render_template('report_results.html', clubs=clubs, rooms=rooms, meetings=filtered_meetings, meetings_data=meetings_with_counts, average_duration=average_duration)

# Run the Flask application
if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    app.run(debug=True)
