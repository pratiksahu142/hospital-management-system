from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from models import db, User


class DatabaseError(Exception):
    pass


def row_to_dict(row):
    return dict(row._mapping)


# Doctor Queries
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


def get_all_doctors_with_dept(id):
    query = text("""
        SELECT doctor.*
        FROM doctor
        WHERE doctor.department_id = :id
    """)
    result = db.session.execute(query, {'id': id})
    return [row_to_dict(row) for row in result]


def get_all_doctors():
    query = text("""
        SELECT *
        FROM doctor
    """)
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]


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
def get_all_departments():
    query = text("SELECT * FROM department")
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]


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


def add_user(username, password, bcrypt, is_admin=False):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, password=hashed_password, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    return user.id


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user_by_id(id):
    return User.query.filter_by(id=id).first()


def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        raise DatabaseError("No user found with the given ID")


def get_all_users():
    return User.query.all()
