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

function openPrescriptionModal(appointmentId) {
    document.getElementById('prescriptionAppointmentId').value = appointmentId;

    fetch(`/get_prescription/${appointmentId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('prescription_notes').value = data.prescription_notes || '';
            var prescriptionModal = new bootstrap.Modal(document.getElementById('prescriptionModal'));
            prescriptionModal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load prescription data');
        });
}

document.getElementById('prescriptionForm').addEventListener('submit', function(e) {
    e.preventDefault();
    if (confirm("Are you sure you want to edit this prescription?")) {
        const appointmentId = document.getElementById('prescriptionAppointmentId').value;
        const prescriptionNotes = document.getElementById('prescription_notes').value;

        fetch(`/edit_prescription/${appointmentId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prescription_notes: prescriptionNotes
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Prescription updated successfully');
                var prescriptionModal = bootstrap.Modal.getInstance(document.getElementById('prescriptionModal'));
                prescriptionModal.hide();
            } else {
                alert('Failed to update prescription: ' + data.message);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An error occurred while updating the prescription');
        });
    }
});

function showDiagnosticModal(appointmentId) {
    fetch(`/get_diagnostic/${appointmentId}`)
        .then(response => response.json())
        .then(diagnostics => {
            const diagnosticList = document.getElementById('diagnosticList');
            diagnosticList.innerHTML = '';
            diagnostics.forEach(diagnostic => {
                diagnosticList.innerHTML += `
                    <div id="diagnostic${diagnostic.id}" class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">${diagnostic.test_name}</h5>
                            <p class="card-text">${diagnostic.test_report}</p>
                            <button onclick="deleteDiagnosticReport(${diagnostic.id})" class="btn btn-danger">Delete</button>
                        </div>
                    </div>
                `;
            });

            // Add the "Add a report" button with w-100 class
            diagnosticList.innerHTML += `
                <button type="button" class="btn btn-primary w-100 mt-2" onclick="openAddDiagnosticModal(${appointmentId})">
                    Add a report
                </button>
            `;

            const showDiagnosticModal = new bootstrap.Modal(document.getElementById('showDiagnosticModal'));
            showDiagnosticModal.show();
        })
        .catch(error => console.error('Error:', error));
}


function openAddDiagnosticModal(appointmentId) {
    const showDiagnosticModal = bootstrap.Modal.getInstance(document.getElementById('showDiagnosticModal'));
    showDiagnosticModal.hide();

    // Set the appointment_id in the form
    document.getElementById('diagnosticAppointmentId').value = appointmentId;

    const addDiagnosticModal = new bootstrap.Modal(document.getElementById('addDiagnosticModal'));
    addDiagnosticModal.show();
}

// Add Diagnostic
document.getElementById('addDiagnosticForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/add_diagnostic', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Diagnostic added successfully');
            const addDiagnosticModal = bootstrap.Modal.getInstance(document.getElementById('addDiagnosticModal'));
            addDiagnosticModal.hide();
            showDiagnosticModal(formData.get('appointment_id'));
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
});

// Delete Diagnostic Report
function deleteDiagnosticReport(id) {
    if (confirm('Are you sure you want to delete this diagnostic report?')) {
        fetch(`/delete_diagnostic/${id}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`diagnostic${id}`).remove();
                    alert('Diagnostic report deleted successfully');
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => console.error('Error:', error));
    }
}