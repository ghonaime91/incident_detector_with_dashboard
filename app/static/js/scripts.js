
// Toggle notification dropdown visibility
document.getElementById('notificationBtn').addEventListener('click', function () {
    const dropdown = document.getElementById('notifDropdown');
    dropdown.classList.toggle('hidden');
    // Reset the notification count to 0 when the notification icon is clicked
    document.getElementById('notifCount').textContent = '0';
});

// Close dropdown when clicking outside
document.addEventListener('click', function (e) {
    const btn = document.getElementById('notificationBtn');
    const dropdown = document.getElementById('notifDropdown');
    if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});

const socket = io();

// Handle new incident notification
socket.on('new_incident_notification', function(data) {
    const incidentId = data.incident_id;
    const locationName = data.location_name;
    const latitude = data.latitude;
    const longitude = data.longitude;
    const incidentUrl = data.incident_url;

    // Create the message with the location name
    const message = `New incident reported at ${locationName} (Lat: ${latitude}, Lon: ${longitude})`;

    // Show toast
    const toast = document.getElementById('toast');
    toast.innerHTML = message;
    toast.classList.remove('hidden');
    toast.classList.add('show');

    setTimeout(function() {
        toast.classList.remove('show');
        toast.classList.add('hidden');
    }, 3000);

    // Add to notification list
    const notifList = document.getElementById('notifList');
    const newNotifItem = document.createElement('li');
    newNotifItem.textContent = message;
    notifList.prepend(newNotifItem);

    // Update notification count
    const notifCount = document.getElementById('notifCount');
    notifCount.textContent = parseInt(notifCount.textContent) + 1;

    // Add new row to incident table
    const tbody = document.getElementById('incidentTableBody');
    const row = document.createElement('tr');
    const now = new Date();
    const formattedDate = now.toLocaleDateString('en-GB');
    
    row.innerHTML = `
        <td><a href="${incidentUrl}">
            ${incidentId}
        </a></td>
        <td>${formattedDate}</td>
        <td>${locationName}</td>
        <td>
            <span class="status-label new">New</span>
        </td>
    `;
    tbody.prepend(row);

    // Add checkbox for new incident to "New Reports" section
    const checkboxList = document.getElementById('checkboxList');
    const listItem = document.createElement('li');
    listItem.innerHTML = `
        <input type="checkbox" id="report${incidentId}" data-id="${incidentId}" onchange="handleCheckboxChange(this)">
        <label for="report${incidentId}">Report ${incidentId}</label>
    `;
    checkboxList.prepend(listItem);
});


