"use strict";
const form = document.getElementById("form");
form.onsubmit = () => {
    const submit_button = document.getElementById("submit-btn");
    submit_button.disabled = true;
    submit_button.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...`
}
