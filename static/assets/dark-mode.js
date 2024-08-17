const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');
const themeToggleBtn = document.getElementById('theme-toggle');

// Fungsi untuk mengatur tema
function setTheme(theme) {
    // Tambahkan kelas transisi
    document.documentElement.classList.add('theme-transition');
    
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
        themeToggleLightIcon.classList.remove('hidden');
        themeToggleDarkIcon.classList.add('hidden');
        localStorage.setItem('color-theme', 'dark');
    } else {
        document.documentElement.classList.remove('dark');
        themeToggleLightIcon.classList.add('hidden');
        themeToggleDarkIcon.classList.remove('hidden');
        localStorage.setItem('color-theme', 'light');
    }
    
    // Hapus kelas transisi setelah transisi selesai
    setTimeout(() => {
        document.documentElement.classList.remove('theme-transition');
    }, 300); // Sesuaikan dengan durasi transisi CSS
}

// Cek preferensi tema saat ini
if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    setTheme('dark');
} else {
    setTheme('light');
}

// Tambahkan event listener untuk tombol toggle
themeToggleBtn.addEventListener('click', function() {
    if (localStorage.getItem('color-theme') === 'dark') {
        setTheme('light');
    } else {
        setTheme('dark');
    }
});