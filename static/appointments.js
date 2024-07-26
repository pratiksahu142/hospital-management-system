let addModal, editModal;

function isValidDate(appointmentDate) {
  const date = new Date(appointmentDate);
  if (isNaN(date.getTime())) {
    return false;
  }

  const currentDate = new Date();

  if (date < currentDate) {
    return false;
  }

  return true;
}

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
      const fromTimeError = document.getElementById("fromTimeError");
      const toTimeError = document.getElementById("toTimeError");
      let hasErrors = false;

      fromTimeError.classList.add("d-none");
      toTimeError.classList.add("d-none");

      if (!isValidDate(data.from_time)) {
        fromTimeError.textContent = "Appointment date cannot be in the past!";
        fromTimeError.classList.remove("d-none");
        hasErrors = true;
      }

      if (!isValidDate(data.to_time)) {
        toTimeError.textContent = "Appointment end time cannot be in the past!";
        toTimeError.classList.remove("d-none");
        hasErrors = true;
      }

      if (!hasErrors) {
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
          } else {
            alert(data.message);
          }
        });
      }
    });

    // Edit appointment form submission
    document.getElementById('editAppointmentForm').addEventListener('submit', function(e) {
      e.preventDefault();
      if (confirm("Are you sure you want to edit this appointment?")) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        const id = data.id;
        const editFromTimeError = document.getElementById("editFromTimeError");
        const editToTimeError = document.getElementById("editToTimeError");
        let hasErrors = false;

        editFromTimeError.classList.add("d-none");
        editToTimeError.classList.add("d-none");

        if (!isValidDate(data.from_time)) {
          editFromTimeError.textContent = "Appointment date cannot be in the past!";
          editFromTimeError.classList.remove("d-none");
          hasErrors = true;
        }

        if (!isValidDate(data.to_time)) {
          editToTimeError.textContent = "Appointment end time cannot be in the past!";
          editToTimeError.classList.remove("d-none");
          hasErrors = true;
        }

        if (!hasErrors) {
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
            } else {
              alert(data.message);
            }
          });
        }
      }
    });


    const searchInput = document.getElementById('searchInput');
    const table = document.getElementById('appointmentsTable');
    const rows = table.getElementsByTagName('tr');

    const fromDateInput = document.getElementById('fromDate');
    const toDateInput = document.getElementById('toDate');

    function filterAppointments() {
        const searchTerm = searchInput.value.toLowerCase();
        const fromDate = fromDateInput.value ? new Date(fromDateInput.value) : null;
        const toDate = toDateInput.value ? new Date(toDateInput.value) : null;

        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;
            let dateInRange = true;

            for (let j = 0; j < cells.length; j++) {
                const cellText = cells[j].textContent.toLowerCase();
                if (cellText.includes(searchTerm)) {
                    found = true;
                }

                // Check if the appointment date is within the selected range
                if (j === 2) {
                    const appointmentDate = new Date(cellText);
                    if (fromDate && appointmentDate < fromDate) {
                        dateInRange = false;
                    }
                    if (toDate && appointmentDate > toDate) {
                        dateInRange = false;
                    }
                }
            }

            if (found && dateInRange) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    }

    searchInput.addEventListener('keyup', filterAppointments);
    fromDateInput.addEventListener('change', filterAppointments);
    toDateInput.addEventListener('change', filterAppointments);

    const fromTimeInput = document.getElementById('from_time');
    const toTimeInput = document.getElementById('to_time');

    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    fromTimeInput.min = now.toISOString().slice(0, 16);

    fromTimeInput.addEventListener('change', function () {
    const fromTime = new Date(fromTimeInput.value);
    const toTime = new Date(fromTime.getTime() + 30 * 60 * 1000);

    toTime.setMinutes(toTime.getMinutes() - toTime.getTimezoneOffset());
    toTimeInput.value = toTime.toISOString().slice(0, 16);
    });

    const editfromTimeInput = document.getElementById('edit_from_time');
    const edittoTimeInput = document.getElementById('edit_to_time');

    editfromTimeInput.addEventListener('change', function () {
    const fromTime = new Date(editfromTimeInput.value);
    const toTime = new Date(fromTime.getTime() + 30 * 60 * 1000);

    toTime.setMinutes(toTime.getMinutes() - toTime.getTimezoneOffset());
    edittoTimeInput.value = toTime.toISOString().slice(0, 16);
    });
});

function openAddModal() {
  addModal.show();
}

function openEditModal(id) {
    const editFromTimeError = document.getElementById("editFromTimeError");
    const editToTimeError = document.getElementById("editToTimeError");

    editFromTimeError.classList.add("d-none");
    editToTimeError.classList.add("d-none");
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

      document.getElementById('edit_from_time').value = appointment.from_time.slice(0, 16);
      document.getElementById('edit_to_time').value = appointment.to_time.slice(0, 16);
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