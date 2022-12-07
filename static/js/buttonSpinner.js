"use strict";
const form = document.getElementById("form");
const body_container = document.getElementById("bodyContainer");
const spinner = document.getElementById("spinner");
form.onsubmit = () => {
    const submit_button = document.getElementById("submit-btn");
    submit_button.disabled = true;
    submit_button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...`
    body_container.classList.add("disabled");
    spinner.classList.toggle("d-none");
}
