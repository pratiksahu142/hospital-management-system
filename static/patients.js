// static/patients.js
let addModal, editModal;

document.addEventListener('DOMContentLoaded', function() {
    addModal = new bootstrap.Modal(document.getElementById('addModal'));
    editModal = new bootstrap.Modal(document.getElementById('editModal'));
});

function openAddModal() {
    addModal.show();
}

function openEditModal(id) {
    fetch(`/get_patient/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('editPatientId').value = id;
            document.getElementById('editName').value = data.name;
            document.getElementById('editPhone').value = data.phone;
            document.getElementById('editEmail').value = data.email;
            document.getElementById('editStreet').value = data.street;
            document.getElementById('editCounty').value = data.county;
            document.getElementById('editCity').value = data.city;
            document.getElementById('editState').value = data.state;
            document.getElementById('editCountry').value = data.country;
            document.getElementById('editZipcode').value = data.zipcode;
            editModal.show();
        });
}

function deletePatient(id) {
    if (confirm('Are you sure you want to delete this patient?')) {
        fetch(`/delete_patient/${id}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
    }
}

document.getElementById('addPatientForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    fetch('/add_patient', {
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

document.getElementById('editPatientForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const id = data.id;

    fetch(`/edit_patient/${id}`, {
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