// Main JavaScript file for MedTech

// Request notification permission
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission().then(function(permission) {
            if (permission === 'granted') {
                console.log('Notification permission granted');
            }
        });
    }
}

// Show notification
function showNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(title, {
            body: body,
            icon: '/static/img/icon.png',
            requireInteraction: true
        });
        
        // Add click handler to focus the window
        notification.onclick = function() {
            window.focus();
            notification.close();
        };
    }
}

// Check and show reminders
function checkReminders() {
    const now = new Date();
    const currentTime = now.getHours() * 60 + now.getMinutes();
    const currentDay = now.getDay(); // 0 = Sunday, 1 = Monday, etc.
    
    // Get all reminders from the page
    const reminders = document.querySelectorAll('.reminder-item');
    reminders.forEach(reminder => {
        const time = reminder.dataset.time;
        const days = reminder.dataset.days.split(',');
        const [hours, minutes] = time.split(':').map(Number);
        const reminderTime = hours * 60 + minutes;
        
        // Check if reminder is for today and if it's time
        if (days.includes(currentDay.toString()) && currentTime === reminderTime) {
            const medicationName = reminder.dataset.medication;
            showNotification(
                'Medication Reminder',
                `Time to take your ${medicationName}`
            );
        }
    });
}

// Initialize notifications
document.addEventListener('DOMContentLoaded', function() {
    // Request notification permission when the page loads
    requestNotificationPermission();
    
    // Check reminders every minute
    setInterval(checkReminders, 60000);
    
    // Initial check
    checkReminders();
});

// Handle medication adherence
function recordAdherence(medicationId, status) {
    fetch(`/medications/${medicationId}/adherence`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `status=${status}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // Update UI to reflect the change
            const adherenceElement = document.querySelector(`#adherence-${medicationId}`);
            if (adherenceElement) {
                adherenceElement.textContent = status;
                adherenceElement.className = `adherence-badge adherence-${status}`;
            }
            // Update the adherence chart if it exists
            if (typeof updateAdherenceChart === 'function') {
                updateAdherenceChart();
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Handle OCR for prescription images
function handlePrescriptionUpload(input) {
    if (input.files && input.files[0]) {
        const formData = new FormData();
        formData.append('image', input.files[0]);
        
        fetch('/medications/ocr', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.medication_name) {
                document.getElementById('name').value = data.medication_name;
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 