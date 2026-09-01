/* SewaGhar UI helpers: theme switching, toasts, reveal animations, misc. */
(function () {
  'use strict';

  /* ---------- Theme ---------- */
  // The initial theme is applied by a tiny inline script in <head> (before CSS
  // paints) to avoid a flash; this wires up the toggle buttons.
  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem('sg-theme', theme); } catch (e) { /* private mode */ }
  }

  window.sgToggleTheme = function () {
    applyTheme(currentTheme() === 'dark' ? 'light' : 'dark');
  };

  /* ---------- Password visibility toggles ---------- */
  // Usage: <button type="button" class="sg-pass-toggle" data-target="inputId">
  function wirePasswordToggles() {
    document.querySelectorAll('.sg-pass-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var input = document.getElementById(btn.getAttribute('data-target'));
        if (!input) return;
        var icon = btn.querySelector('i');
        if (input.type === 'password') {
          input.type = 'text';
          if (icon) icon.className = 'bi bi-eye';
        } else {
          input.type = 'password';
          if (icon) icon.className = 'bi bi-eye-slash';
        }
      });
    });
  }

  /* ---------- Toast messages ---------- */
  function wireToasts() {
    var stack = document.getElementById('sg-toast-stack');
    if (!stack) return;
    var toasts = stack.querySelectorAll('.sg-toast');
    toasts.forEach(function (toast, i) {
      setTimeout(function () {
        toast.classList.add('is-hiding');
        setTimeout(function () { toast.remove(); }, 400);
      }, 3800 + i * 300);
    });
  }

  /* ---------- Reveal on scroll ---------- */
  function wireReveal() {
    var items = document.querySelectorAll('.sg-reveal');
    if (!items.length) return;
    if (!('IntersectionObserver' in window)) return;
    document.documentElement.classList.add('sg-anim');
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    items.forEach(function (el) { observer.observe(el); });
  }

  /* ---------- Back to top ---------- */
  function wireBackToTop() {
    var btn = document.createElement('button');
    btn.id = 'sgBackToTop';
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Back to top');
    btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    document.body.appendChild(btn);
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    window.addEventListener('scroll', function () {
      btn.classList.toggle('show', window.scrollY > 350);
    }, { passive: true });
  }

  document.addEventListener('DOMContentLoaded', function () {
    wirePasswordToggles();
    wireToasts();
    wireReveal();
    wireBackToTop();
  });
})();
