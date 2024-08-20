document.addEventListener('DOMContentLoaded', function() {
    // Fungsi untuk menampilkan modal
    function showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            document.body.classList.add('overflow-hidden');
        }
    }

    // Fungsi untuk menyembunyikan modal
    function hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            document.body.classList.remove('overflow-hidden');
        }
    }

    // Event listener untuk tombol yang membuka modal
    document.querySelectorAll('[data-modal-target]').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-target');
            showModal(modalId);
        });
    });

    // Event listener untuk tombol yang menutup modal
    document.querySelectorAll('[data-modal-hide]').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-hide');
            hideModal(modalId);
        });
    });

    // Menutup modal jika mengklik di luar modal
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('fixed') && event.target.classList.contains('inset-0')) {
            const modalId = event.target.parentElement.id;
            hideModal(modalId);
        }
    });

    // Inisialisasi dropdown
    const userMenuButton = document.getElementById('user-menu-button-2');
    const userMenu = document.getElementById('dropdown-2');

    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', function() {
            userMenu.classList.toggle('hidden');
        });

        // Menutup dropdown jika mengklik di luar
        document.addEventListener('click', function(event) {
            if (!userMenuButton.contains(event.target) && !userMenu.contains(event.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }
});