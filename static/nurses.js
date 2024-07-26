let addModal, editModal;

function isValidPhoneNumber(phone) {
  return /^\d+$/.test(phone);
}

function isValidNumber(numeric) {
  return /^\d+$/.test(numeric);
}

function validateEmail(email) {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

document.addEventListener("DOMContentLoaded", function () {
  addModal = new bootstrap.Modal(document.getElementById("addModal"));
  editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const searchInput = document.getElementById("searchInput");
  const table = document.getElementById("nursesTable");
  const rows = table.getElementsByTagName("tr");

  document
    .getElementById("addNurseForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(e.target);
      const data = Object.fromEntries(formData.entries());
      const phoneError = document.getElementById("phoneError");
      const zipCodeError = document.getElementById("zipCodeError");
      const addValidEmailError = document.getElementById("addValidEmailError");

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

      if (!(data.email && validateEmail(data.email))) {
        addValidEmailError.textContent = "Enter a valid email!";
        addValidEmailError.classList.remove("d-none");
        hasErrors = true;
      }

      if (!hasErrors) {
        fetch("/add_nurse", {
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
              alert("Email already exists!");
            }
          });
      }
    });

  document
    .getElementById("editNurseForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      if (confirm("Are you sure you want to edit this Nurse's details?")) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        const id = data.id;
        const phoneError = document.getElementById("editPhoneError");
        const zipCodeError = document.getElementById("editZipCodeError");
        const editValidEmailError = document.getElementById(
          "editValidEmailError"
        );
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

        if (!(data.email && validateEmail(data.email))) {
          editValidEmailError.textContent = "Enter a valid email!";
          editValidEmailError.classList.remove("d-none");
          hasErrors = true;
        }

        if (!hasErrors)
          fetch(`/edit_nurse/${id}`, {
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
                alert("Email already exists!" + data.error);
              }
            });
      }
    });

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

function openAddModal() {
  addModal.show();
}

function openEditModal(id) {
  const phoneError = document.getElementById("editPhoneError");
  const zipCodeError = document.getElementById("editZipCodeError");

  phoneError.classList.add("d-none");
  zipCodeError.classList.add("d-none");

  fetch(`/get_nurse/${id}`)
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("editNurseId").value = id;
      const nurse = data.nurse;
      const doctors = data.doctors;
      const editDoctorSelect = document.getElementById('editDoctor');
            editDoctorSelect.innerHTML = doctors.map(doctor =>
              `<option value="${doctor.id}" ${doctor.id == nurse.doctor_id ? 'selected' : ''}>${doctor.name}</option>`
            ).join('');

      document.getElementById("editName").value = nurse.name;
      document.getElementById("editPhone").value = nurse.phone;
      document.getElementById("editEmail").value = nurse.email;
      document.getElementById("editStreet").value = nurse.street;
      document.getElementById("editCounty").value = nurse.county;
      document.getElementById("editCity").value = nurse.city;
      document.getElementById("editState").value = nurse.state;
      document.getElementById("editCountry").value = nurse.country;
      document.getElementById("editZipcode").value = nurse.zipcode;
      editModal.show();
    });
}

function deleteNurse(id) {
  if (
    confirm(
      "Are you sure you want to delete this nurse?"
    )
  ) {
    fetch(`/delete_nurse/${id}`, { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          location.reload();
        }
      });
  }
}
