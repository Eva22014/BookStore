// script.js

document.addEventListener('DOMContentLoaded', () => {
    // Обновление общей стоимости
    function updateTotal() {
        const subtotalElements = document.querySelectorAll('.subtotal');
        let total = 0;

        subtotalElements.forEach(subtotal => {
            total += parseFloat(subtotal.textContent.replace(' ₽', ''));
        });

        document.getElementById('total-price').textContent = total.toFixed(2);
    }

    // Обработка изменения количества товара
    document.querySelectorAll('.quantity-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const action = event.target.dataset.action;
            const itemId = event.target.dataset.id;
            const input = document.querySelector(`[data-id="${itemId}"].quantity-input`);
            let quantity = parseInt(input.value);

            if (action === 'increase') {
                quantity++;
            } else if (action === 'decrease') {
                if (quantity > 1) {
                    quantity--;
                }
            }

            input.value = quantity;

            // Обновление подсуммы
            const price = parseFloat(input.parentElement.nextElementSibling.textContent.replace(' ₽', ''));
            const subtotal = document.querySelector(`[data-id="${itemId}"].subtotal`);
            subtotal.textContent = (quantity * price).toFixed(2) + ' ₽';

            updateTotal();
        });
    });

    // Обработка удаления товара
    document.querySelectorAll('.remove-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const itemId = event.target.dataset.id;
            const item = event.target.closest('.cart-item');
            item.remove();

            updateTotal();
        });
    });

    // Обработка очистки корзины
    document.getElementById('clear-cart').addEventListener('click', () => {
        const cartItems = document.querySelector('.cart-items');
        cartItems.innerHTML = '';
        updateTotal();
    });
});







document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.quantity-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const input = btn.parentElement.querySelector('.quantity-input');
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

    function updateQuantity(id, quantity, input) {
        fetch(`/add_to_cart/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `quantity=${quantity}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                input.value = data.quantity;
                updateSubtotal(id, data.quantity, data.price);
                updateTotal();
            } else if (data.error) {
                alert(data.error);
                fetch(`/check_cart/${id}`)
                    .then(res => res.json())
                    .then(d => input.value = d.quantity);
            }
        });
    }

    function updateSubtotal(id, quantity, price) {
        const subtotalSpan = document.querySelector(`.subtotal[data-id='${id}']`);
        const subtotal = (quantity * price).toFixed(2);
        if (subtotalSpan) {
            subtotalSpan.textContent = `${subtotal} ₽`;
        }
    }

    function updateTotal() {
        let total = 0;
        document.querySelectorAll('.cart-item').forEach(function (item) {
            const qty = parseInt(item.querySelector('.quantity-input').value);
            const price = parseFloat(item.querySelector('.price').textContent.replace('₽', '').trim());
            if (!isNaN(qty) && !isNaN(price)) {
                total += qty * price;
            }
        });
        const totalSpan = document.getElementById('total-price');
        if (totalSpan) {
            totalSpan.textContent = `${total.toFixed(2)} ₽`;
        }
    }
});


