import random
import os
from datetime import datetime, timedelta
from faker import Faker
from models import db, User, Doctor, Address, Patient, Nurse, Appointment, Prescription, Diagnostic, Department
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

def insert_random_departments():
    with app.app_context():
        departments = []
        for name in DEPARTMENTS:
            existing_department = Department.query.filter_by(name=name).first()
            if existing_department:
                departments.append(existing_department)
            else:
                department = Department(name=name)
                db.session.add(department)
                departments.append(department)
        db.session.commit()
        return departments

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

def insert_random_users(num_users):
    for _ in range(num_users):
        username = fake.user_name()
        password = bcrypt.generate_password_hash(fake.password()).decode('utf-8')
        is_admin = random.choice([True, False])
        user = User(username=username, password=password, is_admin=is_admin)
        db.session.add(user)
    db.session.commit()

def insert_random_doctors(num_doctors, departments, addresses):
    with app.app_context():
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

def insert_random_nurses(num_nurses, doctors, addresses):
    for _ in range(num_nurses):
        nurse = Nurse(
            name=fake.name(),
            phone=fake.phone_number(),
            email=fake.email(),
            doctor_id=random.choice(doctors).id,
            address_id=random.choice(addresses).id
        )
        db.session.add(nurse)
    db.session.commit()

def insert_random_appointments(num_appointments, doctors, patients):
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

def insert_random_prescriptions(num_prescriptions, appointments):
    for _ in range(num_prescriptions):
        prescription = Prescription(
            appointment_id=random.choice(appointments).id,
            prescription_notes=fake.text()
        )
        db.session.add(prescription)
    db.session.commit()

def insert_random_diagnostics(num_diagnostics, appointments):
    for _ in range(num_diagnostics):
        diagnostic = Diagnostic(
            appointment_id=random.choice(appointments).id,
            test_name=fake.word(),
            test_report=fake.text()
        )
        db.session.add(diagnostic)
    db.session.commit()

def main():
    with app.app_context():
        departments = insert_random_departments()
        addresses = insert_random_addresses(20)
        insert_random_users(5)
        insert_random_doctors(15, departments, addresses)
        insert_random_patients(20, addresses)

        doctors = Doctor.query.all()
        patients = Patient.query.all()

        insert_random_nurses(10, doctors, addresses)
        insert_random_appointments(30, doctors, patients)

        appointments = Appointment.query.all()
        insert_random_prescriptions(20, appointments)
        insert_random_diagnostics(15, appointments)

if __name__ == '__main__':
    main()