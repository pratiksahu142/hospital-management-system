let addModal, editModal;

function isValidPhoneNumber(phone) {
  return /^\d+$/.test(phone);
}

function isValidNumber(numeric) {
  return /^\d+$/.test(numeric);
}

function isValidDob(dob) {
  const date = new Date(dob);
  console.log(date);
  if (isNaN(date.getTime())) {
    return false;
  }

  const currentDate = new Date();

  if (date > currentDate) {
    return false;
  }

  return true;
}

function validateEmail(email) {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

document.addEventListener("DOMContentLoaded", function () {
  addModal = new bootstrap.Modal(document.getElementById("addModal"));
  editModal = new bootstrap.Modal(document.getElementById("editModal"));
  const searchInput = document.getElementById("searchInput");
  const table = document.getElementById("patientsTable");
  const rows = table.getElementsByTagName("tr");

  document
    .getElementById("addPatientForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(e.target);
      const data = Object.fromEntries(formData.entries());
      const phoneError = document.getElementById("phoneError");
      const zipCodeError = document.getElementById("zipCodeError");
      const dobError = document.getElementById("dobError");
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

      if (!(data.dob && isValidDob(data.dob))) {
        dobError.textContent = "Enter a valid date of birth!";
        dobError.classList.remove("d-none");
        hasErrors = true;
      }

      if (!(data.email && validateEmail(data.email))) {
        addValidEmailError.textContent = "Enter a valid email!";
        addValidEmailError.classList.remove("d-none");
        hasErrors = true;
      }

      if (!hasErrors) {
        fetch("/add_patient", {
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
    .getElementById("editPatientForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      if (confirm("Are you sure you want to edit this Patient's details?")) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        const id = data.id;
        const phoneError = document.getElementById("editPhoneError");
        const zipCodeError = document.getElementById("editZipCodeError");
        const dobError = document.getElementById("editDobError");
        const editValidEmailError = document.getElementById(
          "editValidEmailError"
        );
        let hasErrors = false;

        phoneError.classList.add("d-none");
        zipCodeError.classList.add("d-none");
        dobError.classList.add("d-none");

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

        if (!(data.dob && isValidDob(data.dob))) {
          dobError.textContent = "Enter a valid date of birth!";
          dobError.classList.remove("d-none");
          hasErrors = true;
        }

        if (!(data.email && validateEmail(data.email))) {
          editValidEmailError.textContent = "Enter a valid email!";
          editValidEmailError.classList.remove("d-none");
          hasErrors = true;
        }

        if (!hasErrors)
          fetch(`/edit_patient/${id}`, {
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
  const dobError = document.getElementById("editDobError");

  phoneError.classList.add("d-none");
  zipCodeError.classList.add("d-none");
  dobError.classList.add("d-none");

  fetch(`/get_patient/${id}`)
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("editPatientId").value = id;
      document.getElementById("editName").value = data.name;
      document.getElementById("editDob").value = data.dob;
      document.getElementById("editPhone").value = data.phone;
      document.getElementById("editEmail").value = data.email;
      document.getElementById("editStreet").value = data.street;
      document.getElementById("editCounty").value = data.county;
      document.getElementById("editCity").value = data.city;
      document.getElementById("editState").value = data.state;
      document.getElementById("editCountry").value = data.country;
      document.getElementById("editZipcode").value = data.zipcode;
      editModal.show();
    });
}

function deletePatient(id) {
  if (
    confirm(
      "Are you sure you want to delete this patient? All appointments for this patient will also be DELETED"
    )
  ) {
    fetch(`/delete_patient/${id}`, { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          location.reload();
        }
      });
  }
}
