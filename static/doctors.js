let addModal, editModal;

document.addEventListener("DOMContentLoaded", function () {
  addModal = new bootstrap.Modal(document.getElementById("addModal"));
  editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const searchInput = document.getElementById("searchInput");
  const table = document.getElementById("doctorsTable");
  const rows = table.getElementsByTagName("tr");

  searchInput.addEventListener("keyup", function () {
    const searchTerm = searchInput.value.toLowerCase();

    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const cells = row.getElementsByTagName("td");
      let found = false;

      for (let j = 0; j < cells.length; j++) {
        const cellText = cells[j].textContent.toLowerCase();
        if (cellText.includes(searchTerm)) {
          found = true;
          break;
        }
      }

      if (found) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    }
  });
});

function isValidPhoneNumber(phone) {
  return /^\d+$/.test(phone);
}

function isValidNumber(numeric) {
  return /^\d+$/.test(numeric);
}

function openAddModal() {
  addModal.show();
}

function openEditModal(id) {
    const phoneError = document.getElementById("editPhoneError");
    const zipCodeError = document.getElementById("editZipCodeError");

    phoneError.classList.add("d-none");
    zipCodeError.classList.add("d-none");
  fetch(`/get_doctor/${id}`)
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("editDoctorId").value = id;
      document.getElementById("editName").value = data.name;
      document.getElementById("editPhone").value = data.phone;
      document.getElementById("editEmail").value = data.email;
      // Set the department
      const departmentSelect = document.getElementById("editDepartment");
      for (let i = 0; i < departmentSelect.options.length; i++) {
        if (departmentSelect.options[i].value == data.department_id) {
          departmentSelect.selectedIndex = i;
          break;
        }
      }

      // Set the category
      const categorySelect = document.getElementById("editCategory");
      for (let i = 0; i < categorySelect.options.length; i++) {
        if (categorySelect.options[i].value == data.category) {
          categorySelect.selectedIndex = i;
          break;
        }
      }

      document.getElementById("editExperience").value = data.experience;
      document.getElementById("editDegree").value = data.degree;
      document.getElementById("editStreet").value = data.street;
      document.getElementById("editCounty").value = data.county;
      document.getElementById("editCity").value = data.city;
      document.getElementById("editState").value = data.state;
      document.getElementById("editCountry").value = data.country;
      document.getElementById("editZipcode").value = data.zipcode;
      editModal.show();
    });
}

function deleteDoctor(id) {
  if (confirm("Are you sure you want to delete this doctor?")) {
    fetch(`/delete_doctor/${id}`, { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          location.reload();
        }
      });
  }
}

document
  .getElementById("addDoctorForm")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const phoneError = document.getElementById("phoneError");
    const zipCodeError = document.getElementById("zipCodeError");
    let hasErrors = false;

    if (!(data.phone && isValidPhoneNumber(data.phone))) {
      phoneError.textContent = "Enter a valid phone number!";
      phoneError.classList.remove("d-none");
      hasErrors = true;
    }

    if (!(data.zipcode && isValidNumber(data.zipcode))) {
      zipCodeError.textContent = "Enter a valid zipcode!";
      zipCodeError.classList.remove("d-none");
      hasErrors = true;
    }

    if (!hasErrors) {
      fetch("/add_doctor", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            addModal.hide();
            location.reload();
          } else {
            alert('Email already exists!')
          }
        });
    }
  });

document
  .getElementById("editDoctorForm")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    if (confirm("Are you sure you want to edit this Doctor's details?")) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        const id = data.id;
        const phoneError = document.getElementById("editPhoneError");
        const zipCodeError = document.getElementById("editZipCodeError");
        let hasErrors = false;

        phoneError.classList.add("d-none");
        zipCodeError.classList.add("d-none");

        if (!(data.phone && isValidPhoneNumber(data.phone))) {
          phoneError.textContent = "Enter a valid phone number!";
          phoneError.classList.remove("d-none");
          hasErrors = true;
        }

        if (!(data.zipcode && isValidNumber(data.zipcode))) {
          zipCodeError.textContent = "Enter a valid zipcode!";
          zipCodeError.classList.remove("d-none");
          hasErrors = true;
        }

        if (!hasErrors) {
          fetch(`/edit_doctor/${id}`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.success) {
                editModal.hide();
                location.reload();
              } else {
                alert('Email already exists!')
              }
            });
        }
    }
  });
