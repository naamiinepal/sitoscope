"use strict";

const submit_button = document.getElementById("submit-btn")
const loading = (btn) => () => {
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...`
}

submit_button.onclick = loading(submit_button);