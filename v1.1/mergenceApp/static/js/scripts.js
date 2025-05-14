document.addEventListener('DOMContentLoaded', function () {
    const mainHotlineSelect = document.getElementById('main-hotline');
    const subHotlineDivs = document.querySelectorAll('.hotline-sub');

    mainHotlineSelect.addEventListener('change', function () {
        subHotlineDivs.forEach(div => {
            div.style.display = 'none';
        });

        const selected = this.value;
        const target = document.getElementById(selected);
        if (target) {
            target.style.display = 'block';
        }
    });
});

function closePopup() {
    document.getElementById("popup").style.display = "none";
}
window.onload = function () {
    document.getElementById("popup").style.display = "flex";
};