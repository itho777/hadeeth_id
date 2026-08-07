/**
 * HADEETH.ID — App JS
 * Mobile menu toggle, active nav links, and general UI utilities.
 */
document.addEventListener('DOMContentLoaded', () => {

  // --- Mobile Menu Toggle ---
  const menuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
      const icon = menuBtn.querySelector('[data-menu-icon]');
      if (icon) icon.textContent = mobileMenu.classList.contains('open') ? 'close' : 'menu';
    });
  }

  // --- Mark Active Nav Link ---
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('[data-nav-page]').forEach(link => {
    if (link.dataset.navPage === currentPage) {
      link.classList.add('nav-link-active');
    }
  });

  // --- Copy Hadith Button ---
  document.querySelectorAll('[data-copy-hadith]').forEach(btn => {
    btn.addEventListener('click', () => {
      const arabic = document.querySelector('[data-arabic-text]')?.innerText || '';
      const english = document.querySelector('[data-english-text]')?.innerText || '';
      const text = arabic + '\n\n' + english + '\n\n— HADEETH.ID';
      navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied!';
        setTimeout(() => btn.innerHTML = '<span class="material-symbols-outlined text-[16px]">content_copy</span> Copy', 2000);
      });
    });
  });

  // --- Translation Selector (Hadith Detail page) ---
  document.querySelectorAll('[data-lang-select]').forEach(sel => {
    sel.addEventListener('change', () => {
      // In future: fetch from CDN JSON based on selected language
      console.log('Language changed to:', sel.value, '— will fetch from CDN in production.');
    });
  });

});
