function selectSize(element) {
    // Убираем выделение со всех размеров
    document.querySelectorAll('.size-option').forEach((option) => {
        option.classList.remove('selected');
    });

    // Добавляем выделение на выбранный размер
    element.classList.add('selected');

    // Обновляем цену под названием продукта
    const price = element.getAttribute('data-price');
    const size = element.getAttribute('data-size');
    const titleElement = document.getElementById('product-title');

    if (price) {
        titleElement.innerText = `Выбран размер: ${size} — Цена: ${price}`;
    } else {
        titleElement.innerText = `Выбран размер: ${size} — --`;
    }
}