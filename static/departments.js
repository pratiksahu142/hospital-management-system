let addModal, editModal;

document.addEventListener('DOMContentLoaded', function() {
    addModal = new bootstrap.Modal(document.getElementById('addModal'));
    editModal = new bootstrap.Modal(document.getElementById('editModal'));
});

function openAddModal() {
    addModal.show();
}

function openEditModal(id) {
    fetch(`/get_department/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('editDepartmentId').value = id;
            document.getElementById('editName').value = data.name;
            editModal.show();
        });
}

function deleteDepartment(id) {
    if (confirm('Are you sure you want to delete this Department?')) {
        fetch(`/delete_department/${id}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
    }
}

document.getElementById('addDepartmentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    fetch('/add_department', {
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

document.getElementById('editDepartmentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const id = data.id;

    fetch(`/edit_department/${id}`, {
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