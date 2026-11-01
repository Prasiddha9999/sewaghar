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

  /* ---------- Programmatic toasts ---------- */
  window.sgToast = function (text, iconClass) {
    var stack = document.getElementById('sg-toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'sg-toast-stack';
      stack.id = 'sg-toast-stack';
      stack.setAttribute('aria-live', 'polite');
      document.body.appendChild(stack);
    }
    var toast = document.createElement('div');
    toast.className = 'sg-toast';
    var icon = document.createElement('i');
    icon.className = 'bi ' + (iconClass || 'bi-check-circle-fill');
    var body = document.createElement('div');
    body.textContent = text;
    toast.appendChild(icon);
    toast.appendChild(body);
    stack.appendChild(toast);
    setTimeout(function () {
      toast.classList.add('is-hiding');
      setTimeout(function () { toast.remove(); }, 400);
    }, 6000);
  };

  /* ---------- Live notifications (polling) ---------- */
  // Polls /api/notifications/status every 5s on any page that shows the bell,
  // updates the badge in place and pops a toast when something new arrives.
  function wireNotificationPolling() {
    var bells = document.querySelectorAll('.sg-bell');
    if (!bells.length) return;

    function setBadge(count) {
      bells.forEach(function (bell) {
        var badge = bell.querySelector('.sg-bell-badge');
        if (count > 0) {
          if (!badge) {
            badge = document.createElement('span');
            badge.className = 'sg-bell-badge';
            bell.appendChild(badge);
          }
          badge.textContent = count > 99 ? '99+' : String(count);
        } else if (badge) {
          badge.remove();
        }
      });
    }

    function poll() {
      fetch('/api/notifications/status', { credentials: 'same-origin', headers: { 'Accept': 'application/json' } })
        .then(function (res) {
          var type = res.headers.get('content-type') || '';
          if (!res.ok || type.indexOf('json') === -1) return null;
          return res.json();
        })
        .then(function (data) {
          if (!data) return;
          setBadge(data.count || 0);
          var stored = null;
          try { stored = sessionStorage.getItem('sg-last-note-id'); } catch (e) {}
          if (stored !== null && data.latest_id > parseInt(stored || '0', 10) && data.latest_text) {
            window.sgToast(data.latest_text, 'bi-bell-fill');
          }
          try { sessionStorage.setItem('sg-last-note-id', String(data.latest_id || 0)); } catch (e) {}
        })
        .catch(function () { /* offline or session expired — try again next tick */ });
    }

    poll();
    setInterval(poll, 5000);
  }

  /* ---------- Maps (Leaflet + OpenStreetMap) ---------- */
  var leafletPromise = null;
  window.sgLoadLeaflet = function () {
    if (leafletPromise) return leafletPromise;
    leafletPromise = new Promise(function (resolve, reject) {
      var link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
      document.head.appendChild(link);
      var script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js';
      script.onload = function () { resolve(window.L); };
      script.onerror = reject;
      document.head.appendChild(script);
    });
    return leafletPromise;
  };

  window.sgOsmTiles = function (L) {
    // German OSM community tile server: keyless and open, unlike
    // tile.openstreetmap.org (blocks third-party sites) and CARTO
    // (now watermarks tiles with "API key required").
    return L.tileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
  };

  // Extract lat/lng from an OpenStreetMap or Google Maps URL. Returns null for
  // links without coordinates (e.g. the old default "google.com/maps/").
  window.sgParseMapCoords = function (url) {
    if (!url) return null;
    var m = url.match(/[?&]mlat=(-?\d+\.?\d*)&mlon=(-?\d+\.?\d*)/);
    if (!m) m = url.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/);
    if (!m) m = url.match(/[?&](?:q|ll)=(-?\d+\.\d+),\s*(-?\d+\.\d+)/);
    if (!m) return null;
    var lat = parseFloat(m[1]);
    var lng = parseFloat(m[2]);
    if (isNaN(lat) || isNaN(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) return null;
    return { lat: lat, lng: lng };
  };

  // Read-only mini maps: <div class="sg-map" data-sg-map="{{ order.googlemap }}"></div>
  function wireMiniMaps() {
    var els = document.querySelectorAll('[data-sg-map]');
    if (!els.length) return;
    var pending = [];
    els.forEach(function (el) {
      var coords = window.sgParseMapCoords(el.getAttribute('data-sg-map'));
      if (coords) pending.push({ el: el, coords: coords });
      else el.style.display = 'none';
    });
    if (!pending.length) return;
    window.sgLoadLeaflet().then(function (L) {
      pending.forEach(function (item) {
        var map = L.map(item.el, { scrollWheelZoom: false }).setView([item.coords.lat, item.coords.lng], 16);
        window.sgOsmTiles(L).addTo(map);
        L.marker([item.coords.lat, item.coords.lng]).addTo(map);
      });
    }).catch(function () {
      pending.forEach(function (item) { item.el.style.display = 'none'; });
    });
  }

  /* ---------- CSRF helper ---------- */
  window.sgCsrf = function () {
    var input = document.querySelector('input[name=csrfmiddlewaretoken]');
    if (input) return input.value;
    var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return m ? m[1] : '';
  };

  /* ---------- Clickable star rating ---------- */
  // <div class="sg-star-input" data-target="inputId"> with 5 buttons inside.
  function wireStarInputs() {
    document.querySelectorAll('.sg-star-input').forEach(function (box) {
      var input = document.getElementById(box.getAttribute('data-target'));
      var stars = box.querySelectorAll('button');
      function paint(n) {
        stars.forEach(function (s, i) { s.classList.toggle('on', i < n); });
      }
      stars.forEach(function (star, i) {
        star.addEventListener('click', function () {
          if (input) input.value = i + 1;
          paint(i + 1);
        });
        star.addEventListener('mouseenter', function () { paint(i + 1); });
      });
      box.addEventListener('mouseleave', function () { paint(input ? Number(input.value) || 0 : 0); });
      if (input && input.form) {
        input.form.addEventListener('submit', function (e) {
          if (!input.value) {
            e.preventDefault();
            if (window.sgToast) sgToast('Please tap a star to choose your rating.', 'bi-star');
          }
        });
      }
    });
  }

  /* ---------- Auto refresh (bookings / requests) ---------- */
  // Re-fetches the page every 5s and swaps [data-sg-autorefresh] if it changed.
  function wireAutoRefresh() {
    var el = document.querySelector('[data-sg-autorefresh]');
    if (!el) return;
    setInterval(function () {
      fetch(window.location.href, { credentials: 'same-origin' })
        .then(function (r) { return r.ok ? r.text() : null; })
        .then(function (html) {
          if (!html) return;
          var doc = new DOMParser().parseFromString(html, 'text/html');
          var fresh = doc.querySelector('[data-sg-autorefresh]');
          if (fresh && fresh.innerHTML !== el.innerHTML) el.innerHTML = fresh.innerHTML;
        })
        .catch(function () {});
    }, 5000);
  }

  /* ---------- Notifications auto-read ---------- */
  // On a page marked [data-sg-autoread], mark everything read after 3 seconds
  // of viewing - no clicks needed.
  function wireNotificationAutoRead() {
    var page = document.querySelector('[data-sg-autoread]');
    if (!page) return;
    setTimeout(function () {
      fetch('/api/notifications/mark-all-read', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'X-CSRFToken': window.sgCsrf() }
      }).then(function (res) {
        if (!res.ok) return;
        document.querySelectorAll('.sg-notification-row').forEach(function (row) {
          row.classList.add('is-read');
          var icon = row.querySelector('i.bi-envelope-fill');
          if (icon) icon.className = icon.className.replace('bi-envelope-fill', 'bi-envelope-open');
        });
        var counter = document.getElementById('sg-unread-count');
        if (counter) counter.textContent = '0';
      }).catch(function () {});
    }, 3000);
  }

  /* ---------- Help assistant (Gemini) ---------- */
  function wireAssistant() {
    var root = document.getElementById('sg-assistant');
    if (!root) return;
    var fab = document.getElementById('sg-assistant-fab');
    var panel = document.getElementById('sg-assistant-panel');
    var body = document.getElementById('sg-assistant-body');
    var form = document.getElementById('sg-assistant-form');
    var input = document.getElementById('sg-assistant-input');
    var history = [];

    function addMsg(role, text) {
      var row = document.createElement('div');
      row.className = 'sg-chat-msg ' + (role === 'user' ? 'from-user' : 'from-bot');
      row.textContent = text;
      body.appendChild(row);
      body.scrollTop = body.scrollHeight;
      return row;
    }

    fab.addEventListener('click', function () {
      panel.classList.toggle('open');
      if (panel.classList.contains('open') && !body.children.length) {
        addMsg('assistant', 'Namaste! I am SewaGhar Sahayogi. Ask me anything about booking a service, creating an account, payments or ratings. \u0928\u0947\u092a\u093e\u0932\u0940\u092e\u093e \u092a\u0928\u093f \u0938\u094b\u0927\u094d\u0928 \u0938\u0915\u094d\u0928\u0941\u0939\u0941\u0928\u094d\u091b\u0964');
      }
      if (panel.classList.contains('open')) input.focus();
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var text = input.value.trim();
      if (!text) return;
      input.value = '';
      addMsg('user', text);
      history.push({ role: 'user', text: text });
      var typing = addMsg('assistant', '...');
      fetch('/api/assistant', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history: history.slice(0, -1) })
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          typing.textContent = data.reply || 'Sorry, something went wrong.';
          history.push({ role: 'assistant', text: typing.textContent });
          body.scrollTop = body.scrollHeight;
        })
        .catch(function () { typing.textContent = 'Sorry, I could not reach the assistant. Please try again.'; });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    wirePasswordToggles();
    wireToasts();
    wireReveal();
    wireBackToTop();
    wireNotificationPolling();
    wireMiniMaps();
    wireStarInputs();
    wireAutoRefresh();
    wireNotificationAutoRead();
    wireAssistant();
  });
})();
