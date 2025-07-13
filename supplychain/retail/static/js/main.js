// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Update current year in footer
    document.getElementById('current-year').textContent = new Date().getFullYear();
});

// Dynamic form handling
function addFormEventListener(formClass, callback) {
    document.querySelectorAll(formClass).forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            callback(this);
        });
    });
}

// Example AJAX form submission
addFormEventListener('.ajax-form', function(form) {
    fetch(form.action, {
        method: form.method,
        body: new FormData(form),
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Handle success
        } else {
            // Handle errors
        }
    })
    .catch(error => console.error('Error:', error));
});