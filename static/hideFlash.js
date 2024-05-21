setTimeout(function() {
    var flashContainer = document.getElementById('flash-container');
    if (flashContainer) {
        flashContainer.style.opacity = '0';
        setTimeout(function() {
            flashContainer.remove();
        }, 500);
    }
}, 3000);