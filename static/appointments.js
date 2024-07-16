let addModal, editModal;

document.addEventListener('DOMContentLoaded', function() {
  addModal = new bootstrap.Modal(document.getElementById('addModal'));
  editModal = new bootstrap.Modal(document.getElementById('editModal'));

  const patientInput = document.getElementById('patient');
  const departmentSelect = document.getElementById('department');
  const doctorSelect = document.getElementById('doctor');

  // Add appointment form submission
  document.getElementById('addAppointmentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        console.log(data)

        fetch('/add_appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addModal.hide();
                location.reload();
            }
        });
  });

  // Edit appointment form submission
  document.getElementById('editAppointmentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        const id = data.id;

        fetch(`/edit_appointment/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                editModal.hide();
                location.reload();
            }
        });
  });
    const searchInput = document.getElementById('searchInput');
    const table = document.getElementById('appointmentsTable');
    const rows = table.getElementsByTagName('tr');

    searchInput.addEventListener('keyup', function() {
        const searchTerm = searchInput.value.toLowerCase();

        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;

            for (let j = 0; j < cells.length; j++) {
                const cellText = cells[j].textContent.toLowerCase();
                if (cellText.includes(searchTerm)) {
                    found = true;
                    break;
                }
            }

            if (found) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
});

function openAddModal() {
  addModal.show();
}

function openEditModal(id) {
  fetch(`/get_appointment/${id}`)
    .then(response => response.json())
    .then(data => {
      const appointment = data.appointment;
      const doctors = data.doctors;
      const patients = data.patients;

      document.getElementById('editAppointmentId').value = appointment.id;

      const editPatientSelect = document.getElementById('editPatient');
      editPatientSelect.innerHTML = patients.map(patient =>
        `<option value="${patient.id}" ${patient.id == appointment.patient_id ? 'selected' : ''}>${patient.name}</option>`
      ).join('');

      const editDoctorSelect = document.getElementById('editDoctor');
      editDoctorSelect.innerHTML = doctors.map(doctor =>
        `<option value="${doctor.id}" ${doctor.id == appointment.doctor_id ? 'selected' : ''}>${doctor.name}</option>`
      ).join('');

      document.getElementById('edit_from_time').value = appointment.from_time.slice(0, 16); // Remove seconds
      document.getElementById('edit_to_time').value = appointment.to_time.slice(0, 16); // Remove seconds
      document.getElementById('editNotes').value = appointment.notes;

      const editModal = new bootstrap.Modal(document.getElementById('editModal'));
      editModal.show();
    });
}

function deleteAppointment(id) {
  if (confirm('Are you sure you want to delete this appointment?')) {
          fetch(`/delete_appointment/${id}`, { method: 'POST' })
              .then(response => response.json())
              .then(data => {
                  if (data.success) {
                      location.reload();
                  }
              });
      }
}