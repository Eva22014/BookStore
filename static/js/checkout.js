document.addEventListener('DOMContentLoaded', function() {
    const confirmBtn = document.getElementById('confirm-sale');
    const backBtn = document.getElementById('back-to-cart');
    const paymentSelect = document.getElementById('payment-method');

    backBtn.addEventListener('click', function() {
        window.location.href = "{{ url_for('cart') }}";
    });

    confirmBtn.addEventListener('click', function() {
        const paymentMethod = paymentSelect.value;

        fetch("{{ url_for('process_payment') }}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                payment_method: paymentMethod,
                cart_id: "{{ cart_id }}"
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = "{{ url_for('sale_success') }}?sale_id=" + data.sale_id;
            } else {
                alert('Ошибка: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при оформлении заказа');
        });
    });
});
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Перенаправляем на страницу успешного оформления
                window.location.href = "{{ url_for('sale_success') }}?sale_id=" + data.sale_id;
            } else {
                alert('Ошибка: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при оформлении заказа');
        });
    });
});