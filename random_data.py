import random
import os
from datetime import datetime, timedelta
from faker import Faker
from models import db, User, Doctor, Address, Patient, Appointment, Department
from models import init_app
from flask import Flask
from flask_bcrypt import Bcrypt

fake = Faker()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
init_app(app)

DEPARTMENTS = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Oncology']
CATEGORIES = ['Medicine', 'Surgery', 'Radiologist']
DEGREES = ['PhD', 'PG', 'Masters', 'Bachelors', 'Specialization']

# Generate random departments
def insert_random_departments():
    with app.app_context():
        departments = []
        for name in DEPARTMENTS:
            # Check if the department already exists
            existing_department = Department.query.filter_by(name=name).first()
            if existing_department:
                departments.append(existing_department)
            else:
                department = Department(name=name)
                db.session.add(department)
                departments.append(department)
        db.session.commit()
        return departments

# Generate random addresses
def insert_random_addresses(num_addresses):
    addresses = []
    for _ in range(num_addresses):
        address = Address(
            street=fake.street_address(),
            county=fake.city(),
            city=fake.city(),
            state=fake.state(),
            country=fake.country(),
            zipcode=fake.zipcode()
        )
        db.session.add(address)
        addresses.append(address)
    db.session.commit()
    return addresses

# Generate random users
def insert_random_users(num_users):
    for _ in range(num_users):
        username = fake.user_name()
        password = fake.password()
        is_admin = random.choice([True, False])
        user = User(username=username, password=password, is_admin=is_admin)
        db.session.add(user)
    db.session.commit()

# Generate random doctors
def insert_random_doctors(num_doctors, departments, addresses):
    with app.app_context():
        # Refetch departments to ensure they're attached to the current session
        departments = Department.query.all()
        
        for _ in range(num_doctors):
            doctor = Doctor(
                name=fake.name(),
                phone=fake.phone_number(),
                email=fake.email(),
                department_id=random.choice(departments).id,
                category=random.choice(CATEGORIES),
                experience=random.randint(1, 30),
                degree=random.choice(DEGREES),
                address_id=random.choice(addresses).id
            )
            db.session.add(doctor)
        db.session.commit()

# Generate random patients
def insert_random_patients(num_patients, addresses):
    for _ in range(num_patients):
        patient = Patient(
            name=fake.name(),
            phone=fake.phone_number(),
            email=fake.email(),
            dob=fake.date_of_birth(minimum_age=0, maximum_age=100),
            address_id=random.choice(addresses).id
        )
        db.session.add(patient)
    db.session.commit()

# Generate random appointments
def insert_random_appointments(app, num_appointments, doctors, patients):
    with app.app_context():
        for _ in range(num_appointments):
            from_time = fake.date_time_between(start_date='-1y', end_date='now')
            to_time = from_time + timedelta(minutes=30)
            appointment = Appointment(
                doctor_id=random.choice(doctors).id,
                patient_id=random.choice(patients).id,
                from_time=from_time,
                to_time=to_time,
                notes=fake.text()
            )
            db.session.add(appointment)
        db.session.commit()

# Script execution
def main():
    with app.app_context():
        departments = insert_random_departments()
        addresses = insert_random_addresses(10)
        insert_random_users(5)                
        insert_random_doctors(15, departments, addresses)
        insert_random_patients(10, addresses) 
        
        doctors = Doctor.query.all()
        patients = Patient.query.all()
        
        insert_random_appointments(app, 30, doctors, patients)

if __name__ == '__main__':
    main()
