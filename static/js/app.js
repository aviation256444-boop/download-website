/* AppStore shared UI behaviors */
(function () {
  'use strict';

  // ----- Theme (light / dark) -----
  const root = document.documentElement;
  const stored = localStorage.getItem('appstore-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initial = stored || (prefersDark ? 'dark' : 'light');
  root.setAttribute('data-theme', initial);

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('appstore-theme', theme);
    document.querySelectorAll('[data-theme-icon]').forEach((el) => {
      el.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    });
  }
  setTheme(initial);

  document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      setTheme(next);
    });
  });

  // ----- Password visibility -----
  document.querySelectorAll('[data-password-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-password-toggle');
      const input = document.getElementById(id);
      if (!input) return;
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.innerHTML = show
        ? '<i class="bi bi-eye-slash"></i>'
        : '<i class="bi bi-eye"></i>';
      btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    });
  });

  // ----- Submit loading state -----
  document.querySelectorAll('form[data-loading]').forEach((form) => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('[type="submit"]');
      if (btn) btn.classList.add('loading');
    });
  });

  // ----- Download links: prevent double-click + optional confirm toast -----
  document.querySelectorAll('[data-download-link]').forEach((link) => {
    link.addEventListener('click', (e) => {
      if (link.dataset.busy === '1') {
        e.preventDefault();
        return;
      }
      link.dataset.busy = '1';
      link.classList.add('loading');
      setTimeout(() => {
        link.dataset.busy = '0';
        link.classList.remove('loading');
      }, 2500);
    });
  });

  // ----- Copy to clipboard (share / hash) -----
  document.querySelectorAll('[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const text = btn.getAttribute('data-copy') || '';
      try {
        await navigator.clipboard.writeText(text);
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check2"></i> Copied';
        setTimeout(() => { btn.innerHTML = original; }, 1600);
      } catch (err) {
        console.warn('Copy failed', err);
      }
    });
  });

  // ----- Dropzones -----
  document.querySelectorAll('.dropzone').forEach((zone) => {
    const input = zone.querySelector('input[type="file"]');
    const label = zone.querySelector('.dz-filename');
    if (!input) return;

    const showName = () => {
      if (!label) return;
      if (input.files && input.files[0]) {
        label.textContent = input.files[0].name;
      } else {
        label.textContent = label.dataset.placeholder || 'No file chosen';
      }
    };
    input.addEventListener('change', showName);

    ['dragenter', 'dragover'].forEach((evt) => {
      zone.addEventListener(evt, (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
      });
    });
    ['dragleave', 'drop'].forEach((evt) => {
      zone.addEventListener(evt, (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
      });
    });
    zone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (!files || !files.length) return;
      const dt = new DataTransfer();
      dt.items.add(files[0]);
      input.files = dt.files;
      showName();
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
  });

  // ----- Select all checkboxes (dashboard bulk) -----
  const selectAll = document.getElementById('selectAllApps');
  if (selectAll) {
    selectAll.addEventListener('change', () => {
      document.querySelectorAll('input[name="app_ids"]').forEach((cb) => {
        cb.checked = selectAll.checked;
      });
    });
  }

  // ----- Auto-dismiss alerts after 6s -----
  document.querySelectorAll('.alert-dismissible.auto-dismiss').forEach((el) => {
    setTimeout(() => {
      const btn = el.querySelector('.btn-close');
      if (btn) btn.click();
    }, 6000);
  });

  // Sticky download body class
  if (document.querySelector('.sticky-download')) {
    document.body.classList.add('has-sticky-download');
  }
})();
