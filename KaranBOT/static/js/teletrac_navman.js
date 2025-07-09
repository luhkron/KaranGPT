document.addEventListener("DOMContentLoaded", function () {
    // Fetch and populate trip history
    fetch("/teletrac_navman/trip_history")
        .then(res => res.json())
        .then(data => populateTripHistory(data));

    // Fetch and populate alerts
    fetch("/teletrac_navman/alerts")
        .then(res => res.json())
        .then(data => populateAlerts(data));

    // Fetch and populate vehicles on map
    fetch("/teletrac_navman/vehicles")
        .then(res => res.json())
        .then(data => populateMapAndTrucks(data));

    // Filtering
    document.getElementById("tripFilter").addEventListener("input", function (e) {
        const filter = e.target.value.toLowerCase();
        Array.from(document.querySelectorAll("#tripHistory li")).forEach(li => {
            li.style.display = li.textContent.toLowerCase().includes(filter) ? "" : "none";
        });
    });

    // Customization
    document.getElementById("applyTruckStyle").addEventListener("click", function () {
        const truckId = document.getElementById("truckSelect").value;
        const color = document.getElementById("truckColor").value;
        if (window.truckMarkers && window.truckMarkers[truckId]) {
            window.truckMarkers[truckId].setStyle({ color });
        }
    });
});

function populateTripHistory(trips) {
    const ul = document.getElementById("tripHistory");
    ul.innerHTML = "";
    trips.forEach(trip => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.textContent = `${trip.vehicleName} | ${trip.startTime} - ${trip.endTime}`;
        ul.appendChild(li);
    });
}

function populateAlerts(alerts) {
    const ul = document.getElementById("alerts");
    ul.innerHTML = "";
    alerts.forEach(alert => {
        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-warning";
        li.textContent = `${alert.type}: ${alert.description}`;
        ul.appendChild(li);
    });
}

function populateMapAndTrucks(vehicles) {
    const map = L.map('map').setView([-33.8688, 151.2093], 5); // Sydney by default
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    window.truckMarkers = {};
    const select = document.getElementById("truckSelect");
    select.innerHTML = "";
    vehicles.forEach(vehicle => {
        const marker = L.polyline([[vehicle.lat, vehicle.lon]], { color: "#007bff" }).addTo(map);
        marker.bindPopup(`${vehicle.name}`);
        window.truckMarkers[vehicle.id] = marker;
        const opt = document.createElement("option");
        opt.value = vehicle.id;
        opt.textContent = vehicle.name;
        select.appendChild(opt);
    });
}
