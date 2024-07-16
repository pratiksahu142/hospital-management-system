from sqlalchemy import text

from models import db


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


def edit_doctor(id, data):
    query_doctor = text("""
        UPDATE doctor
        SET name = :name, phone = :phone, email = :email, department_id = :department_id,
            category = :category, experience = :experience, degree = :degree
        WHERE id = :id
    """)
    data['id'] = id
    data['experience'] = int(data['experience'])
    db.session.execute(query_doctor, data)

    query_address = text("""
        UPDATE address
        SET street = :street, county = :county, city = :city, state = :state,
            country = :country, zipcode = :zipcode
        WHERE id = (SELECT address_id FROM doctor WHERE id = :id)
    """)
    db.session.execute(query_address, data)

    db.session.commit()


def delete_doctor(id):
    query = text("""
        DELETE FROM doctor WHERE id = :id
    """)
    db.session.execute(query, {'id': id})
    db.session.commit()


def get_doctor(id):
    query = text("""
        SELECT d.*, a.street, a.county, a.city, a.state, a.country, a.zipcode
        FROM doctor d
        LEFT JOIN address a ON d.address_id = a.id
        WHERE d.id = :id
    """)
    result = db.session.execute(query, {'id': id})
    doctor = result.fetchone()
    if doctor is None:
        return None
    return row_to_dict(doctor)
