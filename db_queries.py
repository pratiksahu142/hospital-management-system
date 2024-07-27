from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from models import db, User


class DatabaseError(Exception):
    # Custom exception for handling database errors.
    pass



# Converts a SQLAlchemy row object to a dictionary.   
# Args:
#     row (Row): SQLAlchemy row object.
# Returns:
#     dict: A dictionary representation of the row.

def row_to_dict(row):
    return dict(row._mapping)


# Get all doctors with their address and department details
# Retrieves all doctors along with their associated department and address details.
    
#     Returns:
#         list of dict: A list of dictionaries where each dictionary contains details of a doctor, their department, and address.
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
#  Retrieves all doctors belonging to a specific department based on department ID.
    
#     Args:
#         id (int): The ID of the department.

#     Returns:
#         list of dict: A list of dictionaries where each dictionary contains details of a doctor
#                       in the specified department.
def get_all_doctors_with_dept(id):
    query = text("""
        SELECT doctor.*
        FROM doctor
        WHERE doctor.department_id = :id
    """)
    result = db.session.execute(query, {'id': id})
    return [row_to_dict(row) for row in result]

# Get all doctors without any additional details
#   Retrieves all doctors without additional details.
    
#     Returns:
#         list of dict: A list of dictionaries where each dictionary contains details of a doctor.
def get_all_doctors():
    query = text("""
        SELECT *
        FROM doctor
    """)
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]

# Add a new doctor with address and other details
    # Adds a new doctor to the database with the provided details, including address.
    
    # Args:
    #     data (dict): A dictionary containing the doctor's details and address.

    # Returns:
    #     int: The ID of the newly added doctor.
    
    # Raises:
    #     DatabaseError: If there is an error adding the doctor or if the email already exists.
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
# Updates the details of an existing doctor.
    
# Args:
#     id (int): The ID of the doctor to be updated.
#     data (dict): A dictionary containing the updated details of the doctor.

# Raises:
#     DatabaseError: If there is an error updating the doctor or if the doctor does not exist.
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
#  Deletes a doctor from the database by their ID.
#     Args:
#         id (int): The ID of the doctor to be deleted.

#     Raises:
#         DatabaseError: If there is an error deleting the doctor or if the doctor does not exist.
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
#  Retrieves the details of a specific doctor by their ID, including address.
    
#     Args:
#         id (int): The ID of the doctor to retrieve.

#     Returns:
#         dict: A dictionary containing the doctor's details and address.

#     Raises:
#         DatabaseError: If there is an error retrieving the doctor or if the doctor does not exist.
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


# Get all nurses with details
#   Retrieves all nurses with details.

#     Returns:
#         list of dict: A list of dictionaries where each dictionary contains details of a nurse.
def get_all_nurses():
    query = text("""
        SELECT n.*, 
               doctor.name AS doctor_name,
               address.street,
               address.county,
               address.city,
               address.state,
               address.country,
               address.zipcode
        FROM nurse n
        LEFT JOIN doctor ON n.doctor_id = doctor.id
        LEFT JOIN address ON n.address_id = address.id
    """)
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]

# Add a new nurse with address and other details
# Adds a new nurse to the database with the provided details, including address.

# Args:
#     data (dict): A dictionary containing the nurse's details and address.

# Returns:
#     int: The ID of the newly added nurse.

# Raises:
#     DatabaseError: If there is an error adding the nurse or if the email already exists.
def add_nurse(data):
    try:
        query_check_email = text("""
            SELECT id FROM nurse WHERE email = :email
        """)
        result_email = db.session.execute(query_check_email, {'email': data['email']})
        existing_nurse = result_email.fetchone()

        if existing_nurse:
            raise DatabaseError("Email already exists in the database.")

        query_address = text("""
            INSERT INTO address (street, county, city, state, country, zipcode)
            VALUES (:street, :county, :city, :state, :country, :zipcode)
            RETURNING id
        """)
        result_address = db.session.execute(query_address, data)
        address_id = result_address.fetchone()[0]

        query_nurse = text("""
            INSERT INTO nurse (name, phone, email, doctor_id, address_id)
            VALUES (:name, :phone, :email, :doctor_id, :address_id)
            RETURNING id
        """)
        data['address_id'] = address_id
        result_nurse = db.session.execute(query_nurse, data)
        nurse_id = result_nurse.fetchone()[0]

        db.session.commit()
        return nurse_id
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error adding nurse: {str(e)}")

# Edit an existing nurse's details
# Updates the details of an existing nurse.

# Args:
#     id (int): The ID of the nurse to be updated.
#     data (dict): A dictionary containing the updated details of the nurse.

# Raises:
#     DatabaseError: If there is an error updating the nurse or if the nurse does not exist.
def edit_nurse(id, data):
    try:
        query_doctor = text("""
            UPDATE nurse
            SET name = :name, phone = :phone, email = :email, doctor_id = :doctor_id
            WHERE id = :id
        """)
        data['id'] = id
        result = db.session.execute(query_doctor, data)

        if result.rowcount == 0:
            raise DatabaseError(f"No nurse found with id {id}")
        query_address = text("""
            UPDATE address
            SET street = :street, county = :county, city = :city, state = :state,
                country = :country, zipcode = :zipcode
            WHERE id = (SELECT address_id FROM nurse WHERE id = :id)
        """)
        db.session.execute(query_address, data)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error editing nurse: {str(e)}")

# Delete a nurse by ID
#  Deletes a nurse from the database by their ID.
#     Args:
#         id (int): The ID of the nurse to be deleted.

#     Raises:
#         DatabaseError: If there is an error deleting the nurse or if the nurse does not exist.
def delete_nurse(id):
    try:
        query = text("""
            DELETE FROM nurse WHERE id = :id
        """)
        db.session.execute(query, {'id': id})

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting nurse: {str(e)}")

# Get a specific nurse's details by ID
#  Retrieves the details of a specific nurse by their ID, including address.

#     Args:
#         id (int): The ID of the nurse to retrieve.

#     Returns:
#         dict: A dictionary containing the nurse's details and address.

#     Raises:
#         DatabaseError: If there is an error retrieving the nurse or if the nurse does not exist.
def get_nurse(id):
    try:
        query = text("""
            SELECT n.*, d.name AS doctor_name, a.street, a.county, a.city, a.state, a.country, a.zipcode
            FROM nurse n
            LEFT JOIN address a ON n.address_id = a.id
            LEFT JOIN doctor d ON n.doctor_id = d.id
            WHERE n.id = :id
        """)
        result = db.session.execute(query, {'id': id})
        nurse = result.fetchone()
        if nurse is None:
            raise DatabaseError(f"No nurse found with id {id}")
        return row_to_dict(nurse)
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving nurse: {str(e)}")


# Patient Queries
# Get all patients with their address details
# Retrieves all patients along with their address details.
    
# Returns:
#     list of dict: A list of dictionaries where each dictionary contains details of a patient
#                   and their address.
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
#  Adds a new patient to the database with the provided details, including address.
    
#     Args:
#         data (dict): A dictionary containing the patient's details and address.

#     Returns:
#         int: The ID of the newly added patient.
    
#     Raises:
#         DatabaseError: If there is an error adding the patient or if the email already exists.
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
#  Updates the details of an existing patient.
    
#     Args:
#         id (int): The ID of the patient to be updated.
#         data (dict): A dictionary containing the updated details of the patient.

#     Raises:
#         DatabaseError: If there is an error updating the patient or if the patient does not exist.
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

#     Deletes a patient from the database by their ID.
    
#     Args:
#         id (int): The ID of the patient to be deleted.

#     Raises:
#         DatabaseError: If there is an error deleting the patient or if the patient does not exist.

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
#     Retrieves the details of a specific patient by their ID, including address.
    
#     Args:
#         id (int): The ID of the patient to retrieve.

#     Returns:
#         dict: A dictionary containing the patient's details and address.

#     Raises:
#         DatabaseError: If there is an error retrieving the patient or if the patient does not exist.
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
# Adds a new department to the database if it does not already exist.
    
# Args:
#     data (dict): A dictionary containing the department name.
        
# Returns:
#     int: The ID of the newly added department.
        
# Raises:
#     DatabaseError: If a department with the same name already exists or if there is an error adding the department.
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
#     Edits the details of an existing department by its ID.
    
#     Args:
#         id (int): The ID of the department to edit.
#         data (dict): A dictionary containing the new department name.
        
#     Raises:
#         DatabaseError: If a department with the same name already exists or if there is an error editing the department.
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
    
    # Deletes a department from the database by its ID.
    
    # Args:
    #     id (int): The ID of the department to delete.
        
    # Raises:
    #     DatabaseError: If the department does not exist or if there is an error deleting the department.
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
# Retrieves the details of a specific department by its ID.
    
#     Args:
#         id (int): The ID of the department to retrieve.
        
#     Returns:
#         dict: A dictionary containing the department's details.
        
#     Raises:
#         DatabaseError: If the department does not exist or if there is an error retrieving the department.
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
# Retrieves all appointments along with associated doctor and patient details.
    
#     Returns:
#         list: A list of dictionaries, each containing details of an appointment along with the doctor's and patient's names and IDs.
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

#  Adds a new appointment to the database after checking for conflicts.
    
#     Args:
#         doctor_id (int): The ID of the doctor for the appointment.
#         patient_id (int): The ID of the patient for the appointment.
#         from_time (datetime): The start time of the appointment.
#         to_time (datetime): The end time of the appointment.
#         notes (str): Additional notes for the appointment.
        
#     Returns:
#         dict: A dictionary with success status and the ID of the newly added appointment.
        
#     Raises:
#         DatabaseError: If there is an error adding the appointment or if a conflicting appointment exists.
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

#  Edits an existing appointment, checking for conflicts and updating its details.
    
#     Args:
#         appointment_id (int): The ID of the appointment to edit.
#         doctor_id (int): The ID of the doctor for the appointment.
#         patient_id (int): The ID of the patient for the appointment.
#         from_time (datetime): The new start time of the appointment.
#         to_time (datetime): The new end time of the appointment.
#         notes (str): The new notes for the appointment.
        
#     Returns:
#         dict: A dictionary with success status and the ID of the updated appointment.
        
#     Raises:
#         DatabaseError: If there is an error editing the appointment or if a conflicting appointment exists.
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

# Deletes an appointment from the database by its ID.
    
#     Args:
#         id (int): The ID of the appointment to delete.
        
#     Raises:
#         DatabaseError: If the appointment does not exist or if there is an error deleting the appointment.
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

#  Deletes all appointments associated with a specific doctor by their ID.
    
#     Args:
#         id (int): The ID of the doctor whose appointments are to be deleted.
        
#     Raises:
#         DatabaseError: If there is an error deleting the appointments.
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

#   Deletes all appointments associated with a specific patient by their ID.
    
#     Args:
#         id (int): The ID of the patient whose appointments are to be deleted.
        
#     Raises:
#         DatabaseError: If there is an error deleting the appointments.
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

#   Retrieves the details of a specific appointment by its ID.
    
#     Args:
#         id (int): The ID of the appointment to retrieve.
        
#     Returns:
#         dict: A dictionary containing the appointment's details.
        
#     Raises:
#         DatabaseError: If the appointment does not exist or if there is an error retrieving the appointment.   
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


# Add a new prescription
#  Adds a new blank prescription to the database for an appointment

#     Args:
#        id: Appointment ID for which prescription is added

#     Returns:
#         int: The ID of the newly added prescription.

#     Raises:
#         DatabaseError: If there is an error adding the prescription
def add_prescription(id):
    try:
        prescription_notes = ''
        data = {
            'appointment_id': id,
            'prescription_notes': prescription_notes
        }
        query_prescription = text("""
            INSERT INTO prescription (appointment_id, prescription_notes)
            VALUES (:appointment_id, :prescription_notes)
            RETURNING id
        """)
        result_prescription = db.session.execute(query_prescription, data)
        prescription_id = result_prescription.fetchone()[0]

        db.session.commit()
        return prescription_id
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error adding prescription: {str(e)}")

# Edit an existing prescription's details for appointment ID
#  Updates the details of an existing prescription.

#     Args:
#         id (int): The ID of the appointment whose prescription is to be updated.
#         data (dict): prescription notes

#     Raises:
#         DatabaseError: If there is an error updating the prescription or if the prescription does not exist.
def edit_prescription_by_appointment_id(id, prescription_notes):
    try:
        data = {
            'appointment_id': id,
            'prescription_notes': prescription_notes
        }
        query_prescription = text("""
            UPDATE prescription
            SET prescription_notes = :prescription_notes
            WHERE appointment_id = :appointment_id
        """)
        db.session.execute(query_prescription, data)

        db.session.commit()
        return {'success': True}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error editing prescription: {str(e)}")

# Delete a prescription by appointment ID

#     Deletes a prescription from the database by their appointment ID.

#     Args:
#         id (int): The appointment ID of the prescription to be deleted.

#     Raises:
#         DatabaseError: If there is an error deleting the prescription or if the prescription does not exist.

def delete_prescription_by_appointment_id(id):
    try:
        query = text("""
            DELETE FROM prescription WHERE appointment_id = :id
        """)
        result = db.session.execute(query, {'id': id})

        if result.rowcount == 0:
            raise DatabaseError(f"No prescription found with id {id}")

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Error deleting prescription: {str(e)}")


# Get a specific prescription's details by ID
#     Retrieves the details of a specific prescription by their ID

#     Args:
#         id (int): The ID of the appointment_id whose prescription to retrieve.

#     Returns:
#         dict: A dictionary containing the prescription's details

#     Raises:
#         DatabaseError: If there is an error retrieving the prescription or if the prescription does not exist.
def get_prescription_by_appointment_id(id):
    try:
        query = text("""
            SELECT *
            FROM prescription
            WHERE prescription.appointment_id = :id
        """)
        result = db.session.execute(query, {'id': id})
        prescription = result.fetchone()
        if prescription is None:
            raise DatabaseError(f"No prescription found for appointment with id {id}")
        return row_to_dict(prescription)
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving prescription: {str(e)}")

# Adds a new user with a hashed password to the database.

#     Args:
#         username (str): The username of the new user.
#         password (str): The plain text password for the new user.
#         bcrypt: The bcrypt object used for hashing passwords.
#         is_admin (bool): Whether the user is an admin. Defaults to False.

#     Returns:
#         int: The ID of the newly created user.

#     Raises:
#         DatabaseError: If there is an error adding the user to the database.
    
def add_user(username, password, bcrypt, is_admin=False):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, password=hashed_password, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    return user.id


# Retrieves a user from the database by their username.

# Args:
#     username (str): The username of the user to retrieve.

# Returns:
#     User: The user object if found, otherwise None.
def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

# Retrieves a user from the database by their ID.

# Args:
#     id (int): The ID of the user to retrieve.

# Returns:
#     User: The user object if found, otherwise None.
def get_user_by_id(id):
    return User.query.filter_by(id=id).first()

# Deletes a user from the database by their ID.

#     Args:
#         user_id (int): The ID of the user to delete.

#     Raises:
#         DatabaseError: If no user is found with the given ID or if there is an error deleting the user.
    
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        raise DatabaseError("No user found with the given ID")


# Retrieves all users from the database.

#     Returns:
#         list: A list of all user objects.
def get_all_users():
    return User.query.all()

# Counts the number of patients per doctor.

#     Returns:
#         list: A list of dictionaries with doctor ID, name, and patient count.
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

# Counts the number of patients per department.

#     Returns:
#         list: A list of dictionaries with department name and patient count.

#     Raises:
#         DatabaseError: If there is an error retrieving the data.
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

# Counts the number of patients on a daily basis.

#     Returns:
#         list: A list of dictionaries with date and patient count.
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

# Counts the number of patients on a monthly basis.

#     Returns:
#         list: A list of dictionaries with month and year, and patient count.
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

# Counts the number of patients on a yearly basis.

#     Returns:
#         list: A list of dictionaries with year and patient count.

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
