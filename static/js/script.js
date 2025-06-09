document.addEventListener('DOMContentLoaded', function () {
    // === Обновление общей стоимости ===
    function updateTotal() {
        let total = 0;
        document.querySelectorAll('.cart-item').forEach(function (item) {
            const qtyInput = item.querySelector('.quantity-input');
            const priceSpan = item.querySelector('.price');

            if (!qtyInput || !priceSpan) return;

            const qty = parseInt(qtyInput.value);
            const priceText = priceSpan.textContent.replace('₽', '').trim();
            const price = parseFloat(priceText);

            if (!isNaN(qty) && !isNaN(price)) {
                total += qty * price;
            }
        });

        const totalSpan = document.getElementById('total-price');
        if (totalSpan) {
            totalSpan.textContent = `${total.toFixed(2)} ₽`;
        }
    }

    // === Изменение количества через кнопки +/- ===
    document.querySelectorAll('.quantity-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const input = btn.closest('.quantity-control').querySelector('.quantity-input');
            const id = btn.dataset.id;
            let value = parseInt(input.value);

            if (btn.dataset.action === 'increase') {
                value++;
            } else if (btn.dataset.action === 'decrease' && value > 1) {
                value--;
            }

            updateQuantity(id, value, input);
        });
    });

    // === Изменение количества вручную ===
    document.querySelectorAll('.quantity-input').forEach(function (input) {
        const id = input.closest('.quantity-control').querySelector('.quantity-btn').dataset.id;

        input.addEventListener('change', function () {
            let value = parseInt(input.value);
            if (isNaN(value) || value < 1) value = 1;
            updateQuantity(id, value, input);
        });

        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                input.blur();
            }
        });
    });

    // === Отправка нового количества на сервер ===
    function updateQuantity(id, quantity, input) {
        fetch(`/add_to_cart/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `quantity=${encodeURIComponent(quantity)}`
        })
        .then(res => {
            if (!res.ok) throw new Error('Сетевая ошибка');
            return res.json();
        })
        .then(data => {
            if (data.success) {
                input.value = data.quantity;
                updateSubtotal(id, data.quantity, data.price);
                updateTotal();
            } else if (data.error) {
                alert(data.error);
                fetch(`/check_cart/${id}`)
                    .then(res => res.json())
                    .then(d => {
                        input.value = d.quantity;
                        updateSubtotal(id, d.quantity, data.price || 0);
                        updateTotal();
                    });
            }
        })
        .catch(err => {
            console.error('Ошибка:', err);
            alert('Не удалось обновить количество. Проверьте соединение.');
        });
    }

    // === Обновление подитога по книге ===
    function updateSubtotal(id, quantity, price) {
        const subtotalSpan = document.querySelector(`.subtotal[data-id='${id}']`);
        if (subtotalSpan) {
            subtotalSpan.textContent = `${(quantity * price).toFixed(2)} ₽`;
        }
    }

    // === Удаление товара из корзины ===
    document.querySelectorAll('.remove-btn').forEach(button => {
        button.addEventListener('click', function (event) {
            const itemId = event.target.dataset.id;
            const item = event.target.closest('.cart-item');
            if (item) item.remove();

            fetch(`/remove_from_cart/${itemId}`, {
                method: 'POST'
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const cartControl = document.querySelector(`.cart-control[data-book-id="${itemId}"]`);
                    if (cartControl) {
                        const addButton = cartControl.querySelector('.add-to-cart');
                        const quantitySpan = cartControl.querySelector('.cart-quantity');
                        if (quantitySpan) quantitySpan.textContent = 0;
                        if (addButton) {
                            addButton.style.display = 'inline';
                            if (quantitySpan) quantitySpan.style.display = 'none';
                        }
                    }
                }
                updateTotal();
            });
        });
    });

    // === Очистка корзины ===
    document.getElementById('clear-cart')?.addEventListener('click', () => {
        if (!confirm('Вы уверены, что хотите очистить корзину?')) return;

        fetch('/clear_cart', {
            method: 'POST'
        })
        .then(res => res.json())
        .then(() => {
            document.querySelectorAll('.cart-item').forEach(item => item.remove());
            updateTotal();

            document.querySelectorAll('.book-item').forEach(bookItem => {
                const bookId = bookItem.getAttribute('data-book-id');
                fetch(`/check_cart/${bookId}`)
                    .then(res => res.json())
                    .then(data => {
                        const cartControl = document.querySelector(`.cart-control[data-book-id="${bookId}"]`);
                        if (cartControl) {
                            const addButton = cartControl.querySelector('.add-to-cart');
                            const quantitySpan = cartControl.querySelector('.cart-quantity');
                            if (quantitySpan) quantitySpan.textContent = 0;
                            if (addButton) {
                                addButton.style.display = 'inline';
                                if (quantitySpan) quantitySpan.style.display = 'none';
                            }
                        }
                    });
            });
        });
    });
});