const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
const approve_btns = document.querySelectorAll('.approve-btn');
const reject_btns = document.querySelectorAll('.reject-btn');
const comment_btns = document.querySelectorAll('.comment-btn');
const approved_toast = document.getElementById('approvedToast');
const rejected_toast = document.getElementById('rejectedToast');
const comment_toast = document.getElementById('commentToast');


const approve = (id) => {
    const url = `/api/samples/slideimage/${id}/`;
    fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({
            id: id,
            approved: true,
            reviewed: true
        }),

    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            if (data["approved"]) {
                const image_div = document.getElementById(`div-${data['image_id']}`);
                console.log(image_div)
                image_div.innerHTML = `
                <small class="card-text text-success">${data['image_id']}</small>
                <span class="badge text-success">
                    <i class="bi bi-check-circle-fill"></i>
                    Approved
                </span>
                <div>
                    <button type="button" class="btn btn-outline-danger btn-sm reject-btn"
                        id="reject-btn-${data['id']}" onclick=reject(${data['id']})>Reject</button>
                </div>
                `
                const bsAlert = new bootstrap.Toast(approved_toast);
                bsAlert.show();
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}


const reject = (id) => {
    const url = `/api/samples/slideimage/${id}/`;
    fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({
            id: id,
            approved: false,
            reviewed: true
        }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            if (!data["approved"]) {
                const image_div = document.getElementById(`div-${data['image_id']}`);
                console.log(image_div)
                image_div.innerHTML = `
                <small class="card-text text-danger">${data['image_id']}</small>
                <span class="badge text-danger">
                    <i class="bi bi-x-circle-fill"></i>
                    Rejected
                </span>
                <div>
                    <button type="button" class="btn btn-outline-success btn-sm approve-btn"
                        id="approve-btn-${data['id']}" onclick=approve(${data['id']})>Approve</button>
                </div>
                `
                const bsAlert = new bootstrap.Toast(rejected_toast);
                bsAlert.show();

            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

const comment = (id) => {
    const url = `/api/samples/slideimage/${id}/`;
    const comment = document.getElementById(`comment-${id}`);
    console.log(comment)
    fetch(url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({
            id: id,
            comment: comment.value,
        }),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Comment:', data);

            const bsAlert = new bootstrap.Toast(comment_toast);
            bsAlert.show();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

approve_btns.forEach(btn => {
    btn.addEventListener('click', () => {
        const btn_id = btn.id;
        const id = btn_id.split('-').slice(-1)[0];
        console.log(id);
        approve(id);
    });
});

reject_btns.forEach(btn => {
    btn.addEventListener('click', () => {
        const btn_id = btn.id;
        const id = btn_id.split('-').slice(-1)[0];
        console.log(id)
        reject(id);
    });
});

comment_btns.forEach(btn => {
    btn.addEventListener('click', () => {
        const btn_id = btn.id;
        const id = btn_id.split('-').slice(-1)[0];
        console.log(id)
        comment(id);
    });
});

// const reviewModal = document.getElementById('reviewModal')
// if (reviewModal) {
//     reviewModal.addEventListener('show.bs.modal', event => {
//         // Button that triggered the modal
//         const button = event.relatedTarget
//         // Extract info from data-bs-* attributes
//         const image_id = button.getAttribute('data-bs-whatever')
//         const action = button.getAttribute('data-bs-review')
//         // If necessary, you could initiate an Ajax request here
//         // and then do the updating in a callback.

//         // Update the modal's content.
//         const modalTitle = reviewModal.querySelector('.modal-title')
//         const modalBodyInput = reviewModal.querySelector('.modal-body input')

//         modalTitle.textContent = `${action.charAt(0).toUpperCase()
//             + action.slice(1)} ${image_id}`
//         modalBodyInput.value = image_id
//         modalBodyInput.disabled = true

//         const submitButton = reviewModal.querySelector('.modal-footer button #action')
//         submitButton.value = action.charAt(0).toUpperCase()
//             + action.slice(1)
//     })
// }