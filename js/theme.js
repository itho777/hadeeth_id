/**
 * HADEETH.ID — Theme Manager
 * Handles dark/light mode toggle with localStorage persistence.
 */
(function () {
  const STORAGE_KEY = 'hadeeth-theme';
  const html = document.documentElement;

  // Apply theme from storage immediately (before render) to prevent flash
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    html.classList.add('dark');
  }

  function getTheme() {
    return html.classList.contains('dark') ? 'dark' : 'light';
  }

  function setTheme(theme) {
    if (theme === 'dark') {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
    localStorage.setItem(STORAGE_KEY, theme);
    updateIcons();
  }

  function toggleTheme() {
    setTheme(getTheme() === 'dark' ? 'light' : 'dark');
  }

  function updateIcons() {
    const isDark = getTheme() === 'dark';
    document.querySelectorAll('[data-theme-icon]').forEach(el => {
      el.textContent = isDark ? 'light_mode' : 'dark_mode';
    });
  }

  // Expose globally
  window.HadeethTheme = { toggle: toggleTheme, get: getTheme, set: setTheme };

  // Bind buttons after DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-toggle-theme]').forEach(btn => {
      btn.addEventListener('click', toggleTheme);
    });
    updateIcons();
  });
})();
