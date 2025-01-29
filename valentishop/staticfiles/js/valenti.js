// Подсветка активного элемента при выборе
document.querySelectorAll('.radio-option input').forEach(radio => {
    radio.addEventListener('change', function () {
        document.querySelectorAll('.radio-option').forEach(option => {
            option.classList.remove('active');
        });
        this.parentElement.classList.add('active');
    });
});