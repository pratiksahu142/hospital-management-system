python3 -m venv venv

source venv/bin/activate

pip install Flask Flask-SQLAlchemy

pip install Flask-WTF
pip install email_validator
pip install dash-bootstrap-components


Doctors:
Name
Phone
Email
Department
Category - [Surgery, Medicine, Diagnostics]
Experience
Degree
Address

Patients:
Name
Phone
Email
Address

Appointments:
AppointmentId
DoctorId
PatientId
FromTime
ToTime
Notes

Department:
Name

Address:
Street
County
City
State
Country
Zipcode



Todo:

- complete department table with another page for its crud - done
- try replacing the sqlalchemy methods with SQL queries
