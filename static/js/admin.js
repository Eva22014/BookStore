document.addEventListener('DOMContentLoaded', function() {
    // Мобильное меню
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth > 768) return;

            e.preventDefault();
            const menu = this.nextElementSibling;
            const isOpen = menu.style.display === 'block';

            // Закрываем все открытые меню
            document.querySelectorAll('.dropdown-content').forEach(item => {
                item.style.display = 'none';
            });

            // Открываем текущее, если было закрыто
            if (!isOpen) {
                menu.style.display = 'block';
            }
        });
    });

    // Закрытие меню при клике вне его
    document.addEventListener('click', function(e) {
        if (window.innerWidth > 768) return;

        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-content').forEach(menu => {
                menu.style.display = 'none';
            });
        }
    });
});