/* Generator/static/Generator/js/details.js */

/* Handle Dynamic Event Blocks and Time Slots */

document.addEventListener('DOMContentLoaded', () => {
    let eventIndex = 0;
    const addEventButton = document.getElementById('addEventButton');
    const eventsContainer = document.getElementById('events-container');

    addEventButton.addEventListener('click', () => {
        const currentEventIndex = eventIndex;
        // Create a new event block container.
        const eventDiv = document.createElement('div');
        eventDiv.classList.add('event-block');

        // Build the event block HTML.
        eventDiv.innerHTML = `
            <button type="button" class="remove-event-btn">X</button>
            <h2>New Event</h2>
            <label>Event Name:</label>
            <input type="text" name="event_${currentEventIndex}_name" placeholder="e.g. My Event" required><br><br>
            <label>Time Slot Mode:</label>
            <label>
                <input type="radio" name="event_${currentEventIndex}_mode" value="single" checked> Single
            </label>
            <label>
                <input type="radio" name="event_${currentEventIndex}_mode" value="split"> Split (2 parts)
            </label>
            <br><br>
            <!-- Container for time slots for this event -->
            <div id="time-slots-${currentEventIndex}"></div>
            <button type="button" class="addTimeSlotBtn btn-secondary">Add Time Slot Group</button>
            <hr>
        `;

        // Add Remove Event button functionality.
        eventDiv.querySelector('.remove-event-btn').addEventListener('click', () => {
            eventDiv.remove();
        });

        // Get reference to the time slot container and initialize local counter.
        const timeSlotsContainer = eventDiv.querySelector(`#time-slots-${currentEventIndex}`);
        let timeSlotIndex = 0;

        // When the mode is changed, clear time slots.
        const modeRadios = eventDiv.querySelectorAll(`input[name="event_${currentEventIndex}_mode"]`);
        modeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                timeSlotsContainer.innerHTML = '';
                timeSlotIndex = 0;
            });
        });

        // When "Add Time Slot Group" is clicked.
        eventDiv.querySelector('.addTimeSlotBtn').addEventListener('click', () => {
            // Get the current mode.
            const mode = eventDiv.querySelector(`input[name="event_${currentEventIndex}_mode"]:checked`).value;
            let groupHTML = '';
            if (mode === 'split') {
                // In split mode, add a group with two rows.
                groupHTML = `
                    <div class="time-slot-group">
                        <div class="time-slot-row">
                            <label>Part 1 - Day:</label>
                            <select name="event_${currentEventIndex}_slot_${timeSlotIndex}_first_day" required>
                                <option value="">Select Day</option>
                                <option value="Sun">Sun</option>
                                <option value="Mon">Mon</option>
                                <option value="Tue">Tue</option>
                                <option value="Wed">Wed</option>
                                <option value="Thu">Thu</option>
                                <option value="Fri">Fri</option>
                                <option value="Sat">Sat</option>
                            </select>
                            <label>From:</label>
                            <input type="time" name="event_${currentEventIndex}_slot_${timeSlotIndex}_first_start" required>
                            <label>To:</label>
                            <input type="time" name="event_${currentEventIndex}_slot_${timeSlotIndex}_first_end" required>
                        </div>
                        <div class="time-slot-row">
                            <label>Part 2 - Day:</label>
                            <select name="event_${currentEventIndex}_slot_${timeSlotIndex}_second_day" required>
                                <option value="">Select Day</option>
                                <option value="Sun">Sun</option>
                                <option value="Mon">Mon</option>
                                <option value="Tue">Tue</option>
                                <option value="Wed">Wed</option>
                                <option value="Thu">Thu</option>
                                <option value="Fri">Fri</option>
                                <option value="Sat">Sat</option>
                            </select>
                            <label>From:</label>
                            <input type="time" name="event_${currentEventIndex}_slot_${timeSlotIndex}_second_start" required>
                            <label>To:</label>
                            <input type="time" name="event_${currentEventIndex}_slot_${timeSlotIndex}_second_end" required>
                        </div>
                    </div>
                `;
            } else {
                // Single mode: add a single row.
                groupHTML = `
                    <div class="time-slot-row">
                        <label>Day:</label>
                        <select name="event_${currentEventIndex}_slot_${timeSlotIndex}_day" required>
                            <option value="">Select Day</option>
                            <option value="Sun">Sun</option>
                            <option value="Mon">Mon</option>
                            <option value="Tue">Tue</option>
                            <option value="Wed">Wed</option>
                            <option value="Thu">Thu</option>
                            <option value="Fri">Fri</option>
                            <option value="Sat">Sat</option>
                        </select>
                        <label>From:</label>
                        <input type="time" name="event_${currentEventIndex}_slot_${timeSlotIndex}_start" required>
                        <label>To:</label>
                        <input type="time" name="event_${currentEventIndex}_slot_${timeSlotIndex}_end" required>
                    </div>
                `;
            }
            timeSlotsContainer.insertAdjacentHTML('beforeend', groupHTML);
            timeSlotIndex++;
        });

        // Append the event block and increment the global counter.
        eventsContainer.appendChild(eventDiv);
        eventIndex++;
    });
});