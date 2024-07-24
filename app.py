import os
from datetime import datetime
from functools import wraps

import yaml
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt

import db_queries
from models import init_app

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_app(app)


def load_config():
    with open('configurations/config.yml', 'r') as config_file:
        return yaml.safe_load(config_file)


config = load_config()
doctor_categories = config['doctor_categories']
admin_username = config['admin_username']
admin_password = config['admin_password']


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db_queries.get_user_by_username(username)
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db_queries.get_user_by_username(username):
            flash('Username already exists', 'danger')
        else:
            if username == admin_username:
                db_queries.add_user(username, password, bcrypt, True)
            else:
                db_queries.add_user(username, password, bcrypt)
            flash('Account created successfully', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/admin')
@login_required
def admin():
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    users = db_queries.get_all_users()
    return render_template('admin.html', users=users)


@app.route('/admin/create_user', methods=['POST'])
@login_required
def admin_create_user(data=None, bypass_admin_check=False):
    if not bypass_admin_check and not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    if data is None:
        data = request.json

    try:
        is_admin = data.get('is_admin') in [True, 'true', 'on', 1]
        user_id = db_queries.add_user(data['username'], data['password'], bcrypt, is_admin)
        return jsonify({'success': True, 'id': user_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/delete_user/<int:id>', methods=['POST'])
@login_required
def admin_delete_user(id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    try:
        db_queries.delete_user(id)
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No user found" in str(e) else 500


@app.route('/doctors')
@login_required
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
        # Delete all appointments for this doctor, cascading delete
        db_queries.delete_appointments_for_doctor(id)

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
@login_required
def patients():
    saved_patients = db_queries.get_all_patients()
    for patient in saved_patients:
        patient['dob'] = datetime.fromisoformat(patient['dob'])
    return render_template('patients.html', patients=saved_patients)


@app.route('/get_patients')
def get_patients():
    saved_patients = db_queries.get_all_patients()
    for patient in saved_patients:
        patient['dob'] = datetime.fromisoformat(patient['dob'])
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
        # Delete all appointments for this patient, cascading delete
        db_queries.delete_appointments_for_patient(id)

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
@login_required
def appointments():
    saved_appointments = db_queries.get_all_appointments()
    for appointment in saved_appointments:
        appointment['from_time'] = datetime.fromisoformat(appointment['from_time'])
        appointment['to_time'] = datetime.fromisoformat(appointment['to_time'])
    saved_doctors = db_queries.get_all_doctors_with_address_and_dept()
    saved_patients = db_queries.get_all_patients()
    return render_template('appointments.html', appointments=saved_appointments, doctors=saved_doctors,
                           patients=saved_patients)


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
@login_required
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
        # Find all doctors with department_id, first delete all appointments for these doctors,
        # then delete all these doctors to accomplish cascading delete
        doctors = db_queries.get_all_doctors_with_dept(id)
        for doctor in doctors:
            print('Deleting doctor: ' + doctor['name'])
            db_queries.delete_appointments_for_doctor(doctor['id'])
            db_queries.delete_doctor(doctor['id'])

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
