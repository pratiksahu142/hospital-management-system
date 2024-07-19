from datetime import datetime
import yaml
from flask import Flask, render_template, request, jsonify

import db_queries
from models import init_app, db, Doctor, Patient, Appointment, Department

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_app(app)


def load_config():
    with open('configurations/config.yml', 'r') as config_file:
        return yaml.safe_load(config_file)


config = load_config()
doctor_categories = config['doctor_categories']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/doctors')
def doctors():
    saved_doctors = db_queries.get_all_doctors_with_address_and_dept()
    saved_departments = db_queries.get_all_departments()
    return render_template('doctors.html', doctors=saved_doctors, departments=saved_departments,
                           doctor_categories=doctor_categories)


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
    saved_patients = db_queries.get_all_patients()
    return render_template('patients.html', patients=saved_patients)


@app.route('/get_patients')
def get_patients():
    saved_patients = db_queries.get_all_patients()
    return jsonify([{'id': p.id, 'name': p.name} for p in saved_patients])

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
    saved_appointments = db_queries.get_all_appointments()
    for appointment in saved_appointments:
        appointment['from_time'] = datetime.fromisoformat(appointment['from_time'])
        appointment['to_time'] = datetime.fromisoformat(appointment['to_time'])
    saved_doctors = db_queries.get_all_doctors_with_address_and_dept()
    saved_patients = db_queries.get_all_patients()
    return render_template('appointments.html', appointments=saved_appointments, doctors=saved_doctors, patients=saved_patients)


@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    data = request.json
    try:
        result = db_queries.add_appointment(
            int(data['doctor_id']),
            int(data['patient_id']),
            datetime.fromisoformat(data['from_time']),
            datetime.fromisoformat(data['to_time']),
            data['notes']
        )
        if result['success']:
            return jsonify({'success': True, 'id': result['id']})
        else:
            return jsonify({'success': False, 'message': result['message']}), 400
    except db_queries.DatabaseError as e:
        print(str(e))
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/edit_appointment/<int:id>', methods=['POST'])
def edit_appointment(id):
    data = request.json
    try:
        result = db_queries.edit_appointment(
            id,
            int(data['doctor_id']),
            int(data['patient_id']),
            datetime.fromisoformat(data['from_time']),
            datetime.fromisoformat(data['to_time']),
            data['notes']
        )
        if result['success']:
            return jsonify({'success': True, 'id': result['id']})
        else:
            return jsonify({'success': False, 'message': result['message']}), 400
    except db_queries.DatabaseError as e:
        print(str(e))
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/delete_appointment/<int:id>', methods=['POST'])
def delete_appointment(id):
    try:
        db_queries.delete_appointment(id)
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No appointment found" in str(e) else 500


@app.route('/get_appointment/<int:id>')
def get_appointment(id):
    try:
        appointment = db_queries.get_appointment(id)
        saved_doctors = db_queries.get_all_doctors()
        saved_patients = db_queries.get_all_patients()
        return jsonify({
            'appointment': {
                'id': appointment['id'],
                'doctor_id': appointment['doctor_id'],
                'patient_id': appointment['patient_id'],
                'from_time': appointment['from_time'],
                'to_time': appointment['to_time'],
                'notes': appointment['notes']
            },
            'doctors': [{'id': d['id'], 'name': d['name']} for d in saved_doctors],
            'patients': [{'id': p['id'], 'name': p['name']} for p in saved_patients]
        })
    except db_queries.DatabaseError as e:
        return jsonify({'error': str(e)}), 404 if "No appointment found" in str(e) else 500


@app.route('/departments')
def departments():
    saved_departments = db_queries.get_all_departments()
    return render_template('departments.html', departments=saved_departments)


@app.route('/add_department', methods=['POST'])
def add_department():
    data = request.json
    try:
        department_id = db_queries.add_department(data)
        return jsonify({'success': True, 'id': department_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'message': 'Department already exists', 'error': str(e)}), 500


@app.route('/edit_department/<int:id>', methods=['POST'])
def edit_department(id):
    data = request.json
    try:
        department_id = db_queries.edit_department(id, data)
        return jsonify({'success': True, 'id': department_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'message': 'Department already exists', 'error': str(e)}), 500


@app.route('/delete_department/<int:id>', methods=['POST'])
def delete_department(id):
    try:
        db_queries.delete_department(id)
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No department found" in str(e) else 500


@app.route('/get_department/<int:id>')
def get_department(id):
    try:
        department = db_queries.get_department(id)
        return jsonify(department), 200
    except db_queries.DatabaseError as e:
        return jsonify({'error': str(e)}), 404 if "No department found" in str(e) else 500


if __name__ == '__main__':
    app.run(debug=True)
