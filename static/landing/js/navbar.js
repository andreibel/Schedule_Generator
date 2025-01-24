/* static/js/navbar.js */

/* Navbar Toggle for Responsive Menu and Form Toggles */
document.addEventListener('DOMContentLoaded', () => {
    // Toggle Create Schedule Form
    const addScheduleButton = document.getElementById('add-schedule-button');
    const createScheduleForm = document.getElementById('create-schedule-form');

    if (addScheduleButton && createScheduleForm) {
        addScheduleButton.addEventListener('click', () => {
            if (createScheduleForm.style.display === 'none' || createScheduleForm.style.display === '') {
                createScheduleForm.style.display = 'block';
            } else {
                createScheduleForm.style.display = 'none';
            }
        });
    }

    // Toggle Create Event Form (if applicable)
    const addEventButton = document.getElementById('addEventButton');
    const createEventForm = document.getElementById('create-event-form');

    if (addEventButton && createEventForm) {
        addEventButton.addEventListener('click', () => {
            if (createEventForm.style.display === 'none' || createEventForm.style.display === '') {
                createEventForm.style.display = 'block';
            } else {
                createEventForm.style.display = 'none';
            }
        });
    }
});