function validateForm() {
    var label = document.getElementById("label").value;
    var address = document.getElementById("address").value;
    var city = document.getElementById("city").value;
    var postal_code = document.getElementById("postal_code").value;

    if (label.trim() === "" || address.trim() === "" || city.trim() === "" || postal_code.trim() === "") {
        alert("Please fill in all fields.");
        return false;
    }
    return true;
}

var addressData = {
    label: "Home",
    address: "123 Main St",
    city: "Example City",
    postal_code: "12345"
};

function displayAddress(address) {
    var addressInfoContainer = document.getElementById("address-info");
    addressInfoContainer.innerHTML = "<p><strong>Label:</strong> " + address.label + "</p>" +
                                     "<p><strong>Address:</strong> " + address.address + "</p>" +
                                     "<p><strong>City:</strong> " + address.city + "</p>" +
                                     "<p><strong>Postal Code:</strong> " + address.postal_code + "</p>";
}

displayAddress(addressData);
