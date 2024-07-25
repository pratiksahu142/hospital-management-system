from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from models import db, User


class DatabaseError(Exception):
    pass


def row_to_dict(row):
    return dict(row._mapping)


# Get all doctors with their address and department details
def get_all_doctors_with_address_and_dept():
    query = text("""
        SELECT doctor.*, 
               department.name AS department_name,
               address.street,
               address.county,
               address.city,
               address.state,
               address.country,
               address.zipcode
        FROM doctor
        LEFT JOIN department ON doctor.department_id = department.id
        LEFT JOIN address ON doctor.address_id = address.id
    """)
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]


# Get all doctors in a specific department by department ID
def get_all_doctors_with_dept(id):
    query = text("""
        SELECT doctor.*
        FROM doctor
        WHERE doctor.department_id = :id
    """)
    result = db.session.execute(query, {'id': id})
    return [row_to_dict(row) for row in result]

# Get all doctors without any additional details
def get_all_doctors():
    query = text("""
        SELECT *
        FROM doctor
    """)
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]

# Add a new doctor with address and other details
def add_doctor(data):
    try:
        query_check_email = text("""
            SELECT id FROM doctor WHERE email = :email
        """)
        result_email = db.session.execute(query_check_email, {'email': data['email']})
        existing_doctor = result_email.fetchone()

        if existing_doctor:
            raise DatabaseError("Email already exists in the database.")

        query_address = text("""
            INSERT INTO address (street, county, city, state, country, zipcode)
            VALUES (:street, :county, :city, :state, :country, :zipcode)
            RETURNING id
        """)
        result_address = db.session.execute(query_address, data)
        address_id = result_address.fetchone()[0]

        query_doctor = text("""
            INSERT INTO doctor (name, phone, email, department_id, category, experience, degree, address_id)
            VALUES (:name, :phone, :email, :department_id, :category, :experience, :degree, :address_id)
            RETURNING id
        """)
        data['address_id'] = address_id
        data['experience'] = int(data['experience'])
        result_doctor = db.session.execute(query_doctor, data)
        doctor_id = result_doctor.fetchone()[0]

        db.session.commit()
        return doctor_id
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error adding doctor: {str(e)}")

# Edit an existing doctor's details
def edit_doctor(id, data):
    try:

        query_doctor = text("""
            UPDATE doctor
            SET name = :name, phone = :phone, email = :email, department_id = :department_id,
                category = :category, experience = :experience, degree = :degree
            WHERE id = :id
        """)
        data['id'] = id
        data['experience'] = int(data['experience'])
        result = db.session.execute(query_doctor, data)

        if result.rowcount == 0:
            raise DatabaseError(f"No doctor found with id {id}")

        query_address = text("""
            UPDATE address
            SET street = :street, county = :county, city = :city, state = :state,
                country = :country, zipcode = :zipcode
            WHERE id = (SELECT address_id FROM doctor WHERE id = :id)
        """)
        db.session.execute(query_address, data)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error editing doctor: {str(e)}")

# Delete a doctor by ID
def delete_doctor(id):
    try:
        query = text("""
            DELETE FROM doctor WHERE id = :id
        """)
        db.session.execute(query, {'id': id})

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting doctor: {str(e)}")

# Get a specific doctor's details by ID
def get_doctor(id):
    try:
        query = text("""
            SELECT d.*, a.street, a.county, a.city, a.state, a.country, a.zipcode
            FROM doctor d
            LEFT JOIN address a ON d.address_id = a.id
            WHERE d.id = :id
        """)
        result = db.session.execute(query, {'id': id})
        doctor = result.fetchone()
        if doctor is None:
            raise DatabaseError(f"No doctor found with id {id}")
        return row_to_dict(doctor)
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving doctor: {str(e)}")


# Patient Queries
# Get all patients with their address details
def get_all_patients():
    query = text("""
        SELECT patient.*, 
               address.street,
               address.county,
               address.city,
               address.state,
               address.country,
               address.zipcode
        FROM patient
        LEFT JOIN address ON patient.address_id = address.id
    """)
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]

# Add a new patient with address and other details
def add_patient(data):
    try:

        query_check_email = text("""
            SELECT id FROM patient WHERE email = :email
        """)
        result_email = db.session.execute(query_check_email, {'email': data['email']})
        existing_patient = result_email.fetchone()

        if existing_patient:
            raise DatabaseError("Email already exists in the database.")

        query_address = text("""
            INSERT INTO address (street, county, city, state, country, zipcode)
            VALUES (:street, :county, :city, :state, :country, :zipcode)
            RETURNING id
        """)
        result_address = db.session.execute(query_address, data)
        address_id = result_address.fetchone()[0]
        query_patient = text("""
            INSERT INTO patient (name, dob, phone, email, address_id)
            VALUES (:name, :dob, :phone, :email, :address_id)
            RETURNING id
        """)
        data['address_id'] = address_id
        result_patient = db.session.execute(query_patient, data)
        patient_id = result_patient.fetchone()[0]

        db.session.commit()
        return patient_id
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error adding patient: {str(e)}")

# Edit an existing patient's details
def edit_patient(id, data):
    try:

        query_patient = text("""
            UPDATE patient
            SET name = :name, dob = :dob, phone = :phone, email = :email
            WHERE id = :id
        """)
        data['id'] = id
        result = db.session.execute(query_patient, data)

        if result.rowcount == 0:
            raise DatabaseError(f"No patient found with id {id}")

        query_address = text("""
            UPDATE address
            SET street = :street, county = :county, city = :city, state = :state,
                country = :country, zipcode = :zipcode
            WHERE id = (SELECT address_id FROM patient WHERE id = :id)
        """)
        db.session.execute(query_address, data)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error editing patient: {str(e)}")

# Delete a patient by ID
def delete_patient(id):
    try:
        query = text("""
            DELETE FROM patient WHERE id = :id
        """)
        result = db.session.execute(query, {'id': id})

        if result.rowcount == 0:
            raise DatabaseError(f"No patient found with id {id}")

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting patient: {str(e)}")


# Get a specific patient's details by ID
def get_patient(id):
    try:
        query = text("""
            SELECT p.*, a.street, a.county, a.city, a.state, a.country, a.zipcode
            FROM patient p
            LEFT JOIN address a ON p.address_id = a.id
            WHERE p.id = :id
        """)
        result = db.session.execute(query, {'id': id})
        patient = result.fetchone()
        if patient is None:
            raise DatabaseError(f"No patient found with id {id}")
        return row_to_dict(patient)
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving patient: {str(e)}")


# Department Queries
# Get all departments
def get_all_departments():
    query = text("SELECT * FROM department")
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]

# Add a new department
def add_department(data):
    try:

        query_check_department_name = text("""
            SELECT id FROM department WHERE name = :name
        """)
        result_department_name = db.session.execute(query_check_department_name, {'name': data['name']})
        existing_department = result_department_name.fetchone()

        if existing_department:
            raise DatabaseError("Department already exists in the database.")

        query_department = text("""
            INSERT INTO department (name)
            VALUES (:name)
            RETURNING id
        """)
        result_department = db.session.execute(query_department, data)
        department_id = result_department.fetchone()[0]

        db.session.commit()
        return department_id
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error adding department: {str(e)}")

# Edit an existing department's details
def edit_department(id, data):
    try:

        query_check_department_name = text("""
            SELECT id FROM department WHERE name = :name
        """)
        result_department_name = db.session.execute(query_check_department_name, {'name': data['name']})
        existing_department = result_department_name.fetchone()

        if existing_department:
            raise DatabaseError("Department already exists in the database.")

        query_department = text("""
            UPDATE department
            SET name = :name
            WHERE id = :id
        """)
        data['id'] = id
        db.session.execute(query_department, data)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error editing department: {str(e)}")

# Delete a department by ID
def delete_department(id):
    try:
        query = text("""
            DELETE FROM department WHERE id = :id
        """)
        result = db.session.execute(query, {'id': id})

        if result.rowcount == 0:
            raise DatabaseError(f"No department found with id {id}")

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting department: {str(e)}")

# Get a specific department's details by ID
def get_department(id):
    try:
        query = text("""
            SELECT *
            FROM department
            WHERE department.id = :id
        """)
        result = db.session.execute(query, {'id': id})
        department = result.fetchone()
        if department is None:
            raise DatabaseError(f"No department found with id {id}")
        return row_to_dict(department)
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving department: {str(e)}")


# Appointment Queries
def get_all_appointments():
    query = text("""
        SELECT appointment.*, 
               doctor.name AS doctor_name,
               doctor.id AS doctor_id,
               patient.name AS patient_name,
               patient.id AS patient_id
        FROM appointment
        LEFT JOIN doctor ON appointment.doctor_id = doctor.id
        LEFT JOIN patient ON appointment.patient_id = patient.id
    """)
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]

# Add appointment for a speecific doctor, patient and time
def add_appointment(doctor_id, patient_id, from_time, to_time, notes):
    try:
        # Check for conflicting appointments
        conflict_check_query = text("""
        SELECT COUNT(*) 
        FROM appointment 
        WHERE doctor_id = :doctor_id 
        AND (
            (:from_time BETWEEN from_time AND to_time)
            OR (:to_time BETWEEN from_time AND to_time)
            OR (from_time BETWEEN :from_time AND :to_time)
        )
        """)

        result = db.session.execute(conflict_check_query, {
            'doctor_id': doctor_id,
            'from_time': from_time,
            'to_time': to_time
        })

        if result.scalar() > 0:
            return {'success': False, 'message': 'Conflicting appointment exists'}

        # If no conflict, add the new appointment
        insert_query = text("""
        INSERT INTO appointment (doctor_id, patient_id, from_time, to_time, notes)
        VALUES (:doctor_id, :patient_id, :from_time, :to_time, :notes)
        RETURNING id
        """)

        result = db.session.execute(insert_query, {
            'doctor_id': doctor_id,
            'patient_id': patient_id,
            'from_time': from_time,
            'to_time': to_time,
            'notes': notes
        })

        new_id = result.scalar()
        db.session.commit()

        return {'success': True, 'id': new_id}
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error adding an appointment: {str(e)}")

# Edit an existing appointment
def edit_appointment(appointment_id, doctor_id, patient_id, from_time, to_time, notes):
    try:
        # Check for conflicting appointments, excluding the current appointment
        conflict_check_query = text("""
        SELECT COUNT(*) 
        FROM appointment 
        WHERE doctor_id = :doctor_id 
        AND id != :appointment_id
        AND (
            (:from_time BETWEEN from_time AND to_time)
            OR (:to_time BETWEEN from_time AND to_time)
            OR (from_time BETWEEN :from_time AND :to_time)
        )
        """)

        result = db.session.execute(conflict_check_query, {
            'doctor_id': doctor_id,
            'appointment_id': appointment_id,
            'from_time': from_time,
            'to_time': to_time
        })

        if result.scalar() > 0:
            return {'success': False, 'message': 'Conflicting appointment exists'}

        # If no conflict, update the appointment
        update_query = text("""
        UPDATE appointment 
        SET doctor_id = :doctor_id, 
            patient_id = :patient_id, 
            from_time = :from_time, 
            to_time = :to_time, 
            notes = :notes
        WHERE id = :appointment_id
        RETURNING id
        """)

        result = db.session.execute(update_query, {
            'appointment_id': appointment_id,
            'doctor_id': doctor_id,
            'patient_id': patient_id,
            'from_time': from_time,
            'to_time': to_time,
            'notes': notes
        })

        updated_id = result.scalar()
        if updated_id is None:
            return {'success': False, 'message': 'Appointment not found'}

        db.session.commit()

        return {'success': True, 'id': updated_id}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error editing an appointment: {str(e)}")

# Delete an appointment by ID
def delete_appointment(id):
    try:
        query = text("""
            DELETE FROM appointment WHERE id = :id
        """)
        result = db.session.execute(query, {'id': id})

        if result.rowcount == 0:
            raise DatabaseError(f"No appointment found with id {id}")

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting appointment: {str(e)}")

# Delete all appointments for a specific doctor
def delete_appointments_for_doctor(id):
    try:
        query = text("""
            DELETE FROM appointment WHERE doctor_id = :id
        """)
        db.session.execute(query, {'id': id})

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting appointment: {str(e)}")

# Delete all appointments for a specific patient
def delete_appointments_for_patient(id):
    try:
        query = text("""
            DELETE FROM appointment WHERE patient_id = :id
        """)
        db.session.execute(query, {'id': id})
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting appointment: {str(e)}")

# Retrieve details of a specific appointment by ID
def get_appointment(id):
    try:
        query = text("""
            SELECT*
            FROM appointment
            WHERE appointment.id = :id
        """)
        result = db.session.execute(query, {'id': id})
        appointment = result.fetchone()
        if appointment is None:
            raise DatabaseError(f"No appointment found with id {id}")
        return row_to_dict(appointment)
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving appointment: {str(e)}")

# Add a new user with hashed password
def add_user(username, password, bcrypt, is_admin=False):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, password=hashed_password, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    return user.id


# Retrieve a user by username
def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

# Retrieve a user by ID
def get_user_by_id(id):
    return User.query.filter_by(id=id).first()

# Delete a user by ID
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        raise DatabaseError("No user found with the given ID")


# Retrieve all users
def get_all_users():
    return User.query.all()

# Count the number of patients per doctor
def count_patients_per_doctor():
    query = text("""
        SELECT 
            doctor.id AS doctor_id, 
            doctor.name AS doctor_name,
            COUNT(DISTINCT patient.id) AS patient_count
        FROM 
            doctor
        LEFT JOIN 
            appointment ON doctor.id = appointment.doctor_id
        LEFT JOIN 
            patient ON appointment.patient_id = patient.id
        GROUP BY 
            doctor.id, doctor.name
        ORDER BY 
            doctor.id
    """)
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]

# Count the number of patients per department
def count_patients_per_department():
    try:
        query = text("""
        SELECT d.name AS department_name, COUNT(p.id) AS patient_count
        FROM Department d
        LEFT JOIN Doctor doc ON d.id = doc.department_id
        LEFT JOIN Appointment a ON doc.id = a.doctor_id
        LEFT JOIN Patient p ON a.patient_id = p.id
        GROUP BY d.name
        """)
        result = db.session.execute(query)
        rows = result.mappings().all()
        
        data = [{'department_name': row['department_name'], 'patient_count': row['patient_count']} for row in rows]
        return data
    except Exception as e:
        raise DatabaseError(f"An error occurred: {e}")

# Count the number of patients on a daily basis
def count_patients_daily():
    query = text("""
    SELECT DATE(a.from_time) AS date, COUNT(DISTINCT p.id) AS patient_count
    FROM Appointment a
    JOIN Patient p ON a.patient_id = p.id
    GROUP BY DATE(a.from_time)
    ORDER BY DATE(a.from_time)
    """)
    result = db.session.execute(query)
    rows = result.mappings().all()
    return [{'date': row['date'], 'patient_count': row['patient_count']} for row in rows]

# Count the number of patients on a monthly basis
def count_patients_monthly():
    query = text("""
    SELECT strftime('%Y-%m', a.from_time) AS date, COUNT(DISTINCT p.id) AS patient_count
    FROM Appointment a
    JOIN Patient p ON a.patient_id = p.id
    GROUP BY strftime('%Y-%m', a.from_time)
    ORDER BY strftime('%Y-%m', a.from_time)
    """)
    result = db.session.execute(query)
    rows = result.mappings().all()
    return [{'date': row['date'], 'patient_count': row['patient_count']} for row in rows]

# Count the number of patients on a yearly basis
def count_patients_yearly():
    query = text("""
    SELECT strftime('%Y', a.from_time) AS date, COUNT(DISTINCT p.id) AS patient_count
    FROM Appointment a
    JOIN Patient p ON a.patient_id = p.id
    GROUP BY strftime('%Y', a.from_time)
    ORDER BY strftime('%Y', a.from_time)
    """)
    result = db.session.execute(query)
    rows = result.mappings().all()
    return [{'date': row['date'], 'patient_count': row['patient_count']} for row in rows]
