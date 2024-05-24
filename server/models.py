# server/models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# Association table to store many-to-many relationship between employees and meetings
'''

In SQLAlchemy, when dealing with a many-to-many relationship, you don't necessarily need 
to append both sides of the relationship explicitly. Appending on one side is sufficient 
to establish the relationship in the association table. However, doing so on both sides 
ensures that both objects are aware of the relationship, which can be helpful for 
consistency and avoiding bugs in your application.

Usage: 

Appending on One Side: Appending meeting to employee.meetings will automatically create the 
corresponding entry in the employee_meetings table because of the many-to-many relationship 
defined in SQLAlchemy.

Appending on Both Sides: Doing this ensures that both employee and meeting objects are aware 
of each other, which can be useful when accessing the relationship from either side later in 
your application.

# Create an employee and a meeting
employee = Employee(name='John Doe', hire_date='2022-01-01')
meeting = Meeting(topic='Project Kickoff', scheduled_time='2024-05-24 10:00:00', location='Conference Room')

# Establish the relationship from both sides
employee.meetings.append(meeting)
meeting.employees.append(employee)

# Add them to the session and commit
db.session.add(employee)
db.session.add(meeting)
db.session.commit()


For consistency, you can also append both sides, although it is not strictly necessary
'''
employee_meetings = db.Table(
    'employees_meetings',
    metadata,
    db.Column('employee_id', db.Integer, db.ForeignKey(
        'employees.id'), primary_key=True),
    db.Column('meeting_id', db.Integer, db.ForeignKey(
        'meetings.id'), primary_key=True)
)

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    hire_date = db.Column(db.Date)

    # Relationship mapping the employee to related meetings
    meetings = db.relationship(
        'Meeting', secondary=employee_meetings, back_populates='employees')

    # Relationship mapping the employee to related assignments
    assignments = db.relationship(
        'Assignment', back_populates='employee', cascade='all, delete-orphan')

    # Association proxy to get projects for this employee through assignments
    projects = association_proxy('assignments', 'project',
                                 creator=lambda project_obj: Assignment(project=project_obj))

    def __repr__(self):
        return f'<Employee {self.id}, {self.name}, {self.hire_date}>'


class Meeting(db.Model):
    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String)
    scheduled_time = db.Column(db.DateTime)
    location = db.Column(db.String)

    # Relationship mapping the meeting to related employees
    employees = db.relationship(
        'Employee', secondary=employee_meetings, back_populates='meetings')

    def __repr__(self):
        return f'<Meeting {self.id}, {self.topic}, {self.scheduled_time}, {self.location}>'

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    budget = db.Column(db.Integer)

    # Relationship mapping the project to related assignments
    assignments = db.relationship(
        'Assignment', back_populates='project', cascade='all, delete-orphan')

    # Association proxy to get employees for this project through assignments
    employees = association_proxy('assignments', 'employee',
                                  creator=lambda employee_obj: Assignment(employee=employee_obj))

    def __repr__(self):
        return f'<Review {self.id}, {self.title}, {self.budget}>'
    

# Association Model to store many-to-many relationship between employee and project
class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    # Foreign key to store the employee id
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    # Foreign key to store the project id
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    # Relationship mapping the assignment to related employee
    employee = db.relationship('Employee', back_populates='assignments')
    # Relationship mapping the assignment to related project
    project = db.relationship('Project', back_populates='assignments')

    def __repr__(self):
        return f'<Assignment {self.id}, {self.role}, {self.start_date}, {self.end_date}, {self.employee.name}, {self.project.title}>'