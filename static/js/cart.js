// Функция для обновления счетчика корзины
function updateCartCount(count) {
    const cartCountElement = document.querySelector('.cart-count');
    if(cartCountElement) {
        cartCountElement.textContent = count;

        // Анимация при изменении счетчика
        cartCountElement.style.transform = 'scale(1.5)';
        setTimeout(() => {
            cartCountElement.style.transform = 'scale(1)';
        }, 300);
    }
}

// Инициализация обработчиков при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    // Обработчик для кнопок "В корзину"
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            // Останавливаем всплытие события
            e.stopPropagation();

            // Получаем ID книги
            const bookId = this.dataset.bookId;

            // Блокируем кнопку на время запроса
            const originalText = this.textContent;
            this.disabled = true;

            // Отправляем запрос на сервер
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId })
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    updateCartCount(data.cart_count);

                    // Визуальный эффект
                    this.textContent = 'Добавлено!';
                    this.style.backgroundColor = '#4CAF50';

                    setTimeout(() => {
                        this.textContent = originalText;
                        this.style.backgroundColor = '#9747FF';
                        this.disabled = false;
                    }, 1000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.textContent = 'Ошибка!';
                this.style.backgroundColor = '#DB4444';
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.backgroundColor = '#9747FF';
                    this.disabled = false;
                }, 1000);
            });
        });
    });
});