from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from models import db


class DatabaseError(Exception):
    pass


def row_to_dict(row):
    return dict(row._mapping)


def row_to_dict(row):
    return dict(row._mapping)


def get_all_doctors():
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


def get_all_departments():
    query = text("SELECT * FROM department")
    result = db.session.execute(query)
    return [row_to_dict(row) for row in result]


def add_doctor(data):
    try:
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
        result = db.session.execute(query, {'id': id})

        if result.rowcount == 0:
            raise DatabaseError(f"No doctor found with id {id}")

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
        query_address = text("""
            INSERT INTO address (street, county, city, state, country, zipcode)
            VALUES (:street, :county, :city, :state, :country, :zipcode)
            RETURNING id
        """)
        result_address = db.session.execute(query_address, data)
        address_id = result_address.fetchone()[0]

        query_patient = text("""
            INSERT INTO patient (name, phone, email, address_id)
            VALUES (:name, :phone, :email, :address_id)
            RETURNING id
        """)
        data['address_id'] = address_id
        # data['experience'] = int(data['experience'])
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
            SET name = :name, phone = :phone, email = :email
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
