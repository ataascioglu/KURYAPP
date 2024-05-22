function validateForm() {
    var label = document.getElementById('label').value;
    var address = document.getElementById('address').value;
    var city = document.getElementById('city').value;
    var postalCode = document.getElementById('postal_code').value;

    if (label === "" || address === "" || city === "" || postalCode === "") {
        alert("All fields must be filled out");
        return false;
    }
    return true;
}

function displayAddress(address) {
    var addressInfoContainer = document.getElementById("address-info");
    addressInfoContainer.innerHTML = "<p><strong>Label:</strong> " + address.label + "</p>" +
                                     "<p><strong>Address:</strong> " + address.address + "</p>" +
                                     "<p><strong>City:</strong> " + address.city + "</p>" +
                                     "<p><strong>Postal Code:</strong> " + address.postal_code + "</p>";
}

displayAddress(addressData);
