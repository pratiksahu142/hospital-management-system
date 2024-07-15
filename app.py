# app.py
from datetime import datetime

from flask import Flask, render_template, request, jsonify

from models import db, Doctor, Patient, Address, Appointment, Department

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

doctor_categories = ['Medicine', 'Surgery', 'Radiologist']

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/doctors')
def doctors():
    doctors = Doctor.query.all()
    departments = Department.query.all()
    return render_template('doctors.html', doctors=doctors, departments=departments, doctor_categories=doctor_categories)


@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    data = request.json
    address = Address(
        street=data['street'],
        county=data['county'],
        city=data['city'],
        state=data['state'],
        country=data['country'],
        zipcode=data['zipcode']
    )
    db.session.add(address)
    db.session.flush()

    doctor = Doctor(
        name=data['name'],
        phone=data['phone'],
        email=data['email'],
        department_id=data['department_id'],
        category=data['category'],
        experience=int(data['experience']),
        degree=data['degree'],
        address_id=address.id
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify({'success': True, 'id': doctor.id})


@app.route('/edit_doctor/<int:id>', methods=['POST'])
def edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    data = request.json
    doctor.name = data['name']
    doctor.phone = data['phone']
    doctor.email = data['email']
    doctor.department_id = data['department_id']
    doctor.category = data['category']
    doctor.experience = int(data['experience'])
    doctor.degree = data['degree']

    doctor.address.street = data['street']
    doctor.address.county = data['county']
    doctor.address.city = data['city']
    doctor.address.state = data['state']
    doctor.address.country = data['country']
    doctor.address.zipcode = data['zipcode']

    db.session.commit()
    return jsonify({'success': True})


@app.route('/delete_doctor/<int:id>', methods=['POST'])
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/get_doctor/<int:id>')
def get_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    return jsonify({
        'name': doctor.name,
        'phone': doctor.phone,
        'email': doctor.email,
        'department_id': doctor.department_id,
        'category': doctor.category,
        'experience': doctor.experience,
        'degree': doctor.degree,
        'street': doctor.address.street,
        'county': doctor.address.county,
        'city': doctor.address.city,
        'state': doctor.address.state,
        'country': doctor.address.country,
        'zipcode': doctor.address.zipcode
    })


@app.route('/patients')
def patients():
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)


@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = request.json
    address = Address(
        street=data['street'],
        county=data['county'],
        city=data['city'],
        state=data['state'],
        country=data['country'],
        zipcode=data['zipcode']
    )
    db.session.add(address)
    db.session.flush()

    patient = Patient(
        name=data['name'],
        phone=data['phone'],
        email=data['email'],
        address_id=address.id
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({'success': True, 'id': patient.id})


@app.route('/edit_patient/<int:id>', methods=['POST'])
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    data = request.json
    patient.name = data['name']
    patient.phone = data['phone']
    patient.email = data['email']

    patient.address.street = data['street']
    patient.address.county = data['county']
    patient.address.city = data['city']
    patient.address.state = data['state']
    patient.address.country = data['country']
    patient.address.zipcode = data['zipcode']

    db.session.commit()
    return jsonify({'success': True})


@app.route('/delete_patient/<int:id>', methods=['POST'])
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/get_patient/<int:id>')
def get_patient(id):
    patient = Patient.query.get_or_404(id)
    return jsonify({
        'name': patient.name,
        'phone': patient.phone,
        'email': patient.email,
        'street': patient.address.street,
        'county': patient.address.county,
        'city': patient.address.city,
        'state': patient.address.state,
        'country': patient.address.country,
        'zipcode': patient.address.zipcode
    })


@app.route('/appointments')
def appointments():
    appointments = Appointment.query.all()
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    return render_template('appointments.html', appointments=appointments, doctors=doctors, patients=patients)


@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    data = request.json
    appointment = Appointment(
        doctor_id=data['doctor_id'],
        patient_id=data['patient_id'],
        from_time=datetime.fromisoformat(data['from_time']),
        to_time=datetime.fromisoformat(data['to_time']),
        notes=data['notes']
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'success': True, 'id': appointment.id})


@app.route('/edit_appointment/<int:id>', methods=['POST'])
def edit_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    data = request.json
    appointment.doctor_id = data['doctor_id']
    appointment.patient_id = data['patient_id']
    appointment.from_time = datetime.fromisoformat(data['from_time'])
    appointment.to_time = datetime.fromisoformat(data['to_time'])
    appointment.notes = data['notes']
    db.session.commit()
    return jsonify({'success': True})


@app.route('/delete_appointment/<int:id>', methods=['POST'])
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/get_appointment/<int:id>')
def get_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    doctors = Doctor.query.all()
    patients = Patient.query.all()

    return jsonify({
        'appointment': {
            'id': appointment.id,
            'doctor_id': appointment.doctor_id,
            'patient_id': appointment.patient_id,
            'from_time': appointment.from_time.isoformat(),
            'to_time': appointment.to_time.isoformat(),
            'notes': appointment.notes
        },
        'doctors': [{'id': d.id, 'name': d.name} for d in doctors],
        'patients': [{'id': p.id, 'name': p.name} for p in patients]
    })


@app.route('/get_patients')
def get_patients():
    patients = Patient.query.all()
    return jsonify([{'id': p.id, 'name': p.name} for p in patients])


@app.route('/get_doctors_by_department/<department>')
def get_doctors_by_department(department):
    doctors = Doctor.query.filter_by(department=department).all()
    return jsonify([{'id': d.id, 'name': d.name} for d in doctors])


@app.route('/departments')
def departments():
    departments = Department.query.all()
    return render_template('departments.html', departments=departments)


@app.route('/add_department', methods=['POST'])
def add_department():
    data = request.json
    department = Department(
        name=data['name']
    )
    db.session.add(department)
    db.session.commit()
    return jsonify({'success': True, 'id': department.id})


@app.route('/edit_department/<int:id>', methods=['POST'])
def edit_department(id):
    department = Department.query.get_or_404(id)
    data = request.json
    department.name = data['name']

    db.session.commit()
    return jsonify({'success': True})


@app.route('/delete_department/<int:id>', methods=['POST'])
def delete_department(id):
    department = Department.query.get_or_404(id)
    db.session.delete(department)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/get_department/<int:id>')
def get_department(id):
    department = Department.query.get_or_404(id)
    return jsonify({
        'name': department.name
    })


if __name__ == '__main__':
    app.run(debug=True)
