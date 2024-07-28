import logging
import os
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler

import pandas as pd
import plotly.express as px
import yaml
from dash import Dash, dcc, html, Input, Output
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt

import db_queries
from models import init_app

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['LOGS_FOLDER'] = 'logs'

if not os.path.exists(app.config['LOGS_FOLDER']):
    os.makedirs(app.config['LOGS_FOLDER'])

bcrypt = Bcrypt(app)
init_app(app)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler('logs/hospital_app.log', maxBytes=1024 * 1024, backupCount=10)
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)
# Initialize Dash app
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')


# Load configuration
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
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            app.logger.info(f"User '{username}' logged in")
            return redirect(url_for('dashboard'))
        else:
            app.logger.warning(f"Failed login attempt for username '{username}'")
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db_queries.get_user_by_username(username):
            app.logger.warning(f"Failed to create User with username {username}, it already exists")
            flash('Username already exists', 'danger')
        else:
            if username == admin_username:
                db_queries.add_user(username, password, bcrypt, True)
                app.logger.info(f"New User created as an Admin privileged user with username {username}")
            else:
                db_queries.add_user(username, password, bcrypt)
                app.logger.info(f"New User created as a regular user with username {username}")
            flash('Account created successfully', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/logout')
def logout():
    username = session.get('username', 'Unknown user')
    app.logger.info(f"User '{username}' logged out")
    session.pop('user_id', None)
    session.pop('username', None)
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
        app.logger.warning(f"Insufficient privileges for user '{session['username']}' who is trying"
                           f" to create admin user with username {data['username']}")
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    if data is None:
        data = request.json

    try:
        is_admin = data.get('is_admin') in [True, 'true', 'on', 1]
        user_id = db_queries.add_user(data['username'], data['password'], bcrypt, is_admin)
        if is_admin:
            app.logger.info(
                f"User '{session['username']}' user added an Admin privileged user with username {data['username']}")
        else:
            app.logger.info(f"User '{session['username']}' user added a regular user with username {data['username']}")
        return jsonify({'success': True, 'id': user_id}), 201
    except db_queries.DatabaseError as e:
        app.logger.warning(
            f"Unsuccessful attempt by '{session['username']}' to create admin user with username {data['username']}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/delete_user/<int:id>', methods=['POST'])
@login_required
def admin_delete_user(id):
    if not session.get('is_admin'):
        app.logger.warning(f"Insufficient privileges for user '{session['username']}' who is trying"
                           f" to delete user with id {id}")
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    try:
        user_to_delete = db_queries.get_user_by_id(id)
        db_queries.delete_user(id)
        app.logger.warning(f"User '{session['username']}' user deleted with username {user_to_delete.username}")
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        app.logger.warning(f"User '{session['username']}' user not found with id {id}")
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
        app.logger.info(f"User '{session['username']}' added doctor with details: {data}")
        return jsonify({'success': True, 'id': doctor_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/edit_doctor/<int:id>', methods=['POST'])
def edit_doctor_route(id):
    data = request.json
    try:
        previous_doctor = db_queries.get_doctor(id)
        app.logger.info('Previous values of doctor: ' + str(previous_doctor))
        db_queries.edit_doctor(id, data)
        app.logger.warning(f"User '{session['username']}' edited doctor with updated values: {data}")
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No doctor found" in str(e) else 500


@app.route('/delete_doctor/<int:id>', methods=['POST'])
def delete_doctor_route(id):
    try:
        previous_doctor = db_queries.get_doctor(id)
        app.logger.info('Delete in progress for doctor: ' + str(previous_doctor))

        # Delete all appointments for this doctor, cascading delete
        db_queries.delete_appointments_for_doctor(id)

        db_queries.delete_doctor(id)
        app.logger.warning(f"User '{session['username']}' deleted doctor with ID {id} and all related appointments")
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


@app.route('/nurses')
@login_required
def nurses():
    saved_nurses = db_queries.get_all_nurses()
    saved_doctors = db_queries.get_all_doctors()
    return render_template('nurses.html', nurses=saved_nurses, doctors=saved_doctors)


@app.route('/get_nurses')
def get_nurses():
    saved_nurses = db_queries.get_all_nurses()
    return jsonify([{'id': n.id, 'name': n.name} for n in saved_nurses])


@app.route('/add_nurse', methods=['POST'])
def add_nurse():
    data = request.json
    try:
        nurse_id = db_queries.add_nurse(data)
        app.logger.info(f"User '{session['username']}' added nurse with details: {data}")
        return jsonify({'success': True, 'id': nurse_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/edit_nurse/<int:id>', methods=['POST'])
def edit_nurse(id):
    data = request.json
    try:
        previous_nurse = db_queries.get_nurse(id)
        app.logger.info('Previous values of nurse: ' + str(previous_nurse))
        db_queries.edit_nurse(id, data)
        app.logger.warning(f"User '{session['username']}' edited nurse with updated values: {data}")
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No nurse found" in str(e) else 500


@app.route('/delete_nurse/<int:id>', methods=['POST'])
def delete_nurse(id):
    try:
        previous_nurse = db_queries.get_nurse(id)
        app.logger.info('Delete in progress for nurse: ' + str(previous_nurse))

        db_queries.delete_nurse(id)
        app.logger.warning(f"User '{session['username']}' deleted nurse with ID {id} ")
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No nurse found" in str(e) else 500


@app.route('/get_nurse/<int:id>')
def get_nurse(id):
    try:
        nurse = db_queries.get_nurse(id)
        saved_doctors = db_queries.get_all_doctors()
        return jsonify({
            'nurse': nurse,
            'doctors': [{'id': d['id'], 'name': d['name']} for d in saved_doctors]
        })
    except db_queries.DatabaseError as e:
        return jsonify({'error': str(e)}), 404 if "No nurse found" in str(e) else 500


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
        app.logger.info(f"User '{session['username']}' added patient with details: {data}")
        return jsonify({'success': True, 'id': patient_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/edit_patient/<int:id>', methods=['POST'])
def edit_patient(id):
    data = request.json
    try:
        previous_patient = db_queries.get_patient(id)
        app.logger.info('Previous values of patient: ' + str(previous_patient))
        db_queries.edit_patient(id, data)
        app.logger.warning(f"User '{session['username']}' edited patient with updated values: {data}")
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No patient found" in str(e) else 500


@app.route('/delete_patient/<int:id>', methods=['POST'])
def delete_patient(id):
    try:
        previous_patient = db_queries.get_patient(id)
        app.logger.info('Delete in progress for patient: ' + str(previous_patient))

        # Delete all appointments for this patient, cascading delete
        db_queries.delete_appointments_for_patient(id)

        db_queries.delete_patient(id)
        app.logger.warning(f"User '{session['username']}' deleted patient with ID {id} and all related appointments")
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
            db_queries.add_prescription(result['id'])
            app.logger.info(f"User '{session['username']}' successfully created appointment with details {data}")
            return jsonify({'success': True, 'id': result['id']})
        else:
            app.logger.warning(f"User '{session['username']}' tried creating appointment with details {data} "
                               f"but failed due to {result['message']}")
            return jsonify({'success': False, 'message': result['message']}), 400
    except db_queries.DatabaseError as e:
        print(str(e))
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/edit_appointment/<int:id>', methods=['POST'])
def edit_appointment(id):
    data = request.json
    try:
        previous_appointment = db_queries.get_appointment(id)
        app.logger.info('Previous values of appointment: ' + str(previous_appointment))
        result = db_queries.edit_appointment(
            id,
            int(data['doctor_id']),
            int(data['patient_id']),
            datetime.fromisoformat(data['from_time']),
            datetime.fromisoformat(data['to_time']),
            data['notes']
        )
        if result['success']:
            app.logger.info(f"User '{session['username']}' successfully updated appointment with details {data}")
            return jsonify({'success': True, 'id': result['id']})
        else:
            app.logger.warning(f"User '{session['username']}' tried updating appointment with details {data} "
                               f"but failed due to {result['message']}")
            return jsonify({'success': False, 'message': result['message']}), 400
    except db_queries.DatabaseError as e:
        print(str(e))
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/delete_appointment/<int:id>', methods=['POST'])
def delete_appointment(id):
    try:
        previous_appointment = db_queries.get_appointment(id)
        app.logger.info('Delete in progress for appointment: ' + str(previous_appointment))
        db_queries.delete_prescription_by_appointment_id(id)  # Delete associated prescription first, if any
        db_queries.delete_diagnostic_by_appointment_id(id)  # Delete associated diagnostic first, if any
        db_queries.delete_appointment(id)
        app.logger.warning(f"User '{session['username']}' successfully deleted appointment with ID {id}")
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


@app.route('/edit_prescription/<int:id>', methods=['POST'])
def edit_prescription_for_appointment(id):
    data = request.json
    try:
        previous_prescription = db_queries.get_prescription_by_appointment_id(id)
        app.logger.info('Previous values of prescription: ' + str(previous_prescription))
        result = db_queries.edit_prescription_by_appointment_id(
            id,
            data['prescription_notes']
        )
        if result['success']:
            app.logger.info(f"User '{session['username']}' successfully updated prescription with details {data}")
            return jsonify({'success': True})
        else:
            app.logger.warning(f"User '{session['username']}' tried updating prescription with details {data} "
                               f"but failed due to {result['message']}")
            return jsonify({'success': False, 'message': result['message']}), 400
    except db_queries.DatabaseError as e:
        app.logger.warning(f"User '{session['username']}' tried updating prescription with details {data} "
                           f"but failed due to {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/get_prescription/<int:id>')
def get_prescription(id):
    try:
        prescription = db_queries.get_prescription_by_appointment_id(id)
        return jsonify(prescription), 200
    except db_queries.DatabaseError as e:
        return jsonify({'error': str(e)}), 404 if "No prescription found" in str(e) else 500


@app.route('/add_diagnostic', methods=['POST'])
def add_diagnostic():
    try:
        appointment_id = request.form.get('appointment_id')
        test_name = request.form.get('test_name')
        test_report = request.form.get('test_report')
        data = {
            'test_name': test_name,
            'test_report': test_report
        }
        result = db_queries.add_diagnostic(
            int(appointment_id),
            data
        )

        if result['success']:
            app.logger.info(f"User '{session['username']}' successfully added diagnostic with details {test_name}")
            return jsonify({'success': True, 'id': result['id']})
        else:
            app.logger.warning(f"User '{session['username']}' tried adding diagnostic with details {test_name} "
                               f"but failed due to {result['message']}")
            return jsonify({'success': False, 'message': result['message']}), 400
    except db_queries.DatabaseError as e:
        print(str(e))
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/get_diagnostic/<int:id>')
def get_diagnostic(id):
    try:
        diagnostics = db_queries.get_diagnostic_by_appointment_id(id)
        return jsonify(diagnostics), 200
    except db_queries.DatabaseError as e:
        return jsonify({'error': str(e)}), 404 if "No diagnostics found" in str(e) else 500


@app.route('/delete_diagnostic/<int:id>', methods=['POST'])
def delete_diagnostic(id):
    try:
        previous_diagnostic = db_queries.get_diagnostic(id)
        app.logger.info('Delete in progress for diagnostic: ' + str(previous_diagnostic))
        db_queries.delete_diagnostic(id)
        app.logger.warning(f"User '{session['username']}' successfully deleted diagnostic with ID {id}")
        return jsonify({'success': True}), 200
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'error': str(e)}), 404 if "No diagnostic found" in str(e) else 500


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
        app.logger.info(f"User '{session['username']}' successfully created department with details {data}")
        return jsonify({'success': True, 'id': department_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'message': 'Department already exists', 'error': str(e)}), 500


@app.route('/edit_department/<int:id>', methods=['POST'])
def edit_department(id):
    data = request.json
    try:
        previous_department = db_queries.get_department(id)
        app.logger.info('Previous values of department: ' + str(previous_department))
        department_id = db_queries.edit_department(id, data)
        app.logger.info(f"User '{session['username']}' successfully updated department with details {data}")
        return jsonify({'success': True, 'id': department_id}), 201
    except db_queries.DatabaseError as e:
        return jsonify({'success': False, 'message': 'Department already exists', 'error': str(e)}), 500


@app.route('/delete_department/<int:id>', methods=['POST'])
def delete_department(id):
    try:
        previous_department = db_queries.get_department(id)
        app.logger.info('Delete in progress for department: ' + str(previous_department))
        # Find all doctors with department_id, first delete all appointments for these doctors,
        # then delete all these doctors to accomplish cascading delete
        doctors_in_dept = db_queries.get_all_doctors_with_dept(id)
        for doctor in doctors_in_dept:
            print('Deleting doctor: ' + doctor['name'])
            db_queries.delete_appointments_for_doctor(doctor['id'])
            db_queries.delete_doctor(doctor['id'])

        db_queries.delete_department(id)
        app.logger.info(f"User '{session['username']}' successfully deleted department with ID {id}")
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


dash_app.layout = html.Div([
    dcc.Dropdown(
        id='x-axis-column',
        options=[{'label': col, 'value': col} for col in ['Doctor Name', 'Number of Patients']],
        value='Doctor Name',
        placeholder='Select X-axis column'
    ),
    dcc.Dropdown(
        id='y-axis-column',
        options=[{'label': col, 'value': col} for col in ['Doctor Name', 'Number of Patients']],
        value='Number of Patients',
        placeholder='Select Y-axis column'
    ),
    dcc.Graph(id='doctor_patient_histogram'),
    dcc.Graph(id='dept_patient_histogram'),
    dcc.Graph(id='diagnostics_patient_histogram'),
    dcc.Dropdown(
        id='time-frame',
        options=[
            {'label': 'Daily', 'value': 'daily'},
            {'label': 'Monthly', 'value': 'monthly'},
            {'label': 'Yearly', 'value': 'yearly'}
        ],
        value='daily'
    ),
    dcc.Graph(id='time_graph')
])


# Graph for doctor and patient count
@dash_app.callback(
    Output('doctor_patient_histogram', 'figure'),
    Input('x-axis-column', 'value'),
    Input('y-axis-column', 'value')
)
def update_doctor_patient_histogram(x_column, y_column):
    data = db_queries.count_patients_per_doctor()
    df = pd.DataFrame(data)
    print(df.columns)
    df.rename(columns={'doctor_name': 'Doctor Name', 'patient_count': 'Number of Patients'}, inplace=True)

    if x_column not in df.columns:
        x_column = 'Doctor Name'
    if y_column not in df.columns:
        y_column = 'Number of Patients'

    fig = px.histogram(df, x=x_column, y=y_column, title="Histogram of Patients per Doctor")
    return fig


# Number of Patients per Department
@dash_app.callback(
    Output('dept_patient_histogram', 'figure'),
    Input('x-axis-column', 'value')
)
def update_dept_patient_histogram(x_column):
    try:
        data = db_queries.count_patients_per_department()
        df = pd.DataFrame(data)
        df.rename(columns={'department_name': 'Department Name', 'patient_count': 'Number of Patients'}, inplace=True)

        fig = px.histogram(df, x='Department Name', y='Number of Patients', title="Number of Patients per Department")
        return fig

    except Exception as e:
        print(f"Error updating histogram: {e}")
        return {}


@dash_app.callback(
    Output('time_graph', 'figure'),
    Input('time-frame', 'value')
)
def update_time_graph(time_frame):
    if time_frame == 'daily':
        data = db_queries.count_patients_daily()
    elif time_frame == 'monthly':
        data = db_queries.count_patients_monthly()
    elif time_frame == 'yearly':
        data = db_queries.count_patients_yearly()
    else:
        data = []

    df = pd.DataFrame(data)

    fig = px.line(df, x='date', y='patient_count', title=f'Number of Patients {time_frame.capitalize()}')
    return fig

# Histogram for patients with maximum number of diagnostics
@dash_app.callback(
    Output('diagnostics_patient_histogram', 'figure'),
    Input('x-axis-column', 'value')
)
def update_diagnostics_patient_histogram(x_column):
    try:
        data = db_queries.count_top_diagnostics_per_patient(10)
        df = pd.DataFrame(data)
        df.rename(columns={'patient_name': 'Patient Name', 'diagnostics_count': 'Number of Diagnostic Scans'}, inplace=True)

        fig = px.histogram(df, x='Patient Name', y='Number of Diagnostic Scans', title="10 Patients with maximum number of Diagnostic Scans")
        return fig

    except Exception as e:
        print(f"Error updating histogram: {e}")
        return {}

if __name__ == '__main__':
    app.run(debug=True)
