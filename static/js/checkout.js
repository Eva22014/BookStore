document.getElementById('confirm-sale').addEventListener('click', async function() {
    try {
        const paymentMethod = document.getElementById('payment-method').value;
        const cartId = "{{ cart_id }}";

        const response = await fetch("{{ url_for('process_payment') }}", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                payment_method: paymentMethod,
                cart_id: cartId
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, text: ${errorText}`);
        }

        const data = await response.json();

        if (data.success) {
            // Триггерим событие обновления корзины
            $(document).trigger('cartUpdated');
            window.location.href = "{{ url_for('sale_success') }}";
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка: ' + error.message);
    }
});