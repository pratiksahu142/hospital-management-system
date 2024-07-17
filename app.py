from datetime import datetime

from flask import Flask, render_template, request, jsonify
import db_queries
from models import init_app, db, Doctor, Patient, Address, Appointment, Department

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_app(app)

doctor_categories = ['Medicine', 'Surgery', 'Radiologist']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/doctors')
def doctors():
    doctors = db_queries.get_all_doctors()
    departments = db_queries.get_all_departments()
    return render_template('doctors.html', doctors=doctors, departments=departments, doctor_categories=doctor_categories)


@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    data = request.json
    try:
        doctor_id = db_queries.add_doctor(data)
        return jsonify({'success': True, 'id': doctor_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/edit_doctor/<int:id>', methods=['POST'])
def edit_doctor_route(id):
    data = request.json
    try:
        db_queries.edit_doctor(id, data)
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No doctor found" in str(e) else 500


@app.route('/delete_doctor/<int:id>', methods=['POST'])
def delete_doctor_route(id):
    try:
        db_queries.delete_doctor(id)
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No doctor found" in str(e) else 500


@app.route('/get_doctor/<int:id>')
def get_doctor_route(id):
    try:
        doctor = db_queries.get_doctor(id)
        return jsonify(doctor), 200
    except db_queries.DatabaseError as e:
        return jsonify({'error': str(e)}), 404 if "No doctor found" in str(e) else 500


@app.route('/patients')
def patients():
    patients = db_queries.get_all_patients()
    return render_template('patients.html', patients=patients)


@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = request.json
    try:
        patient_id = db_queries.add_patient(data)
        return jsonify({'success': True, 'id': patient_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/edit_patient/<int:id>', methods=['POST'])
def edit_patient(id):
    data = request.json
    try:
        db_queries.edit_patient(id, data)
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No patient found" in str(e) else 500

@app.route('/delete_patient/<int:id>', methods=['POST'])
def delete_patient(id):
    try:
        db_queries.delete_patient(id)
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No patient found" in str(e) else 500

@app.route('/get_patient/<int:id>')
def get_patient(id):
    try:
        doctor = db_queries.get_patient(id)
        return jsonify(doctor), 200
    except db_queries.DatabaseError as e:
        return jsonify({'error': str(e)}), 404 if "No patient found" in str(e) else 500


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
    departments = get_all_departments()
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
