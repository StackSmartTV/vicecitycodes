/* Vice City Codes cookie consent (self-hosted, no third-party CMP).
   Google Consent Mode v2 defaults are set inline in each page <head>
   (everything denied). This file shows the banner, saves the choice,
   and honors Global Privacy Control (GPC) as a Reject. */
(function () {
  'use strict';
  var KEY = 'vcc-consent';
  var es = (document.documentElement.lang || '').toLowerCase().indexOf('es') === 0;
  var gpc = navigator.globalPrivacyControl === true;
  var root = (document.currentScript && document.currentScript.getAttribute('src') || 'consent.js').replace(/consent\.js.*$/, '');
  var privacyUrl = root + (es ? 'es/privacidad.html#cookies' : 'privacy.html#cookies');

  var T = es ? {
    label: 'Aviso de cookies',
    title: 'Cookies y analítica',
    body: 'Usamos Google Analytics para contar visitas solo si lo aceptas. Las cookies publicitarias personalizadas siempre están desactivadas. Puedes cambiar tu elección en cualquier momento con “Configuración de cookies” al pie de la página.',
    gpc: 'Tu navegador envía la señal Global Privacy Control (GPC). La respetamos como un rechazo: la analítica y las cookies publicitarias están desactivadas.',
    accept: 'Aceptar', reject: 'Rechazar', ok: 'Entendido', more: 'Más información'
  } : {
    label: 'Cookie notice',
    title: 'Cookies & analytics',
    body: 'We use Google Analytics to count visits only if you accept. Personalized advertising cookies are always off. You can change your choice any time with “Cookie settings” in the page footer.',
    gpc: 'Your browser sends a Global Privacy Control (GPC) signal. We honor it as a Reject: analytics and advertising cookies stay off.',
    accept: 'Accept', reject: 'Reject', ok: 'OK', more: 'Learn more'
  };

  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function update(granted) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('consent', 'update', {
      analytics_storage: granted ? 'granted' : 'denied',
      ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied'
    });
  }
  function clearGaCookies() {
    var host = location.hostname, parts = host.split('.');
    var domains = ['', host, '.' + host];
    if (parts.length > 1) domains.push('.' + parts.slice(-2).join('.'));
    document.cookie.split(';').forEach(function (c) {
      var name = c.split('=')[0].trim();
      if (name === '_ga' || name.indexOf('_ga_') === 0 || name === '_gid' || name === '_gat') {
        domains.forEach(function (d) {
          document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (d ? '; domain=' + d : '');
        });
      }
    });
  }

  var banner, opener;
  function close() {
    if (!banner) return;
    banner.hidden = true;
    if (opener && document.contains(opener)) opener.focus();
    opener = null;
  }
  function choose(v) {
    save(v);
    update(v === 'granted' && !gpc);
    if (v !== 'granted' || gpc) clearGaCookies();
    close();
  }
  function build() {
    banner = document.createElement('div');
    banner.className = 'cc-banner';
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', T.label);
    banner.hidden = true;
    var h = document.createElement('p'); h.className = 'cc-title'; h.id = 'cc-title'; h.textContent = T.title;
    var p = document.createElement('p'); p.className = 'cc-text'; p.id = 'cc-text';
    p.textContent = (gpc ? T.gpc : T.body) + ' ';
    var a = document.createElement('a'); a.href = privacyUrl; a.textContent = T.more; p.appendChild(a);
    var row = document.createElement('div'); row.className = 'cc-actions';
    function btn(txt, fn) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'cc-btn'; b.textContent = txt;
      b.addEventListener('click', fn); row.appendChild(b); return b;
    }
    if (gpc) {
      btn(T.ok, function () { choose('denied'); });
    } else {
      btn(T.reject, function () { choose('denied'); });
      btn(T.accept, function () { choose('granted'); });
    }
    banner.setAttribute('aria-describedby', 'cc-text');
    banner.appendChild(h); banner.appendChild(p); banner.appendChild(row);
    banner.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
    document.body.appendChild(banner);
  }
  function open(fromEl) {
    if (!banner) build();
    opener = fromEl || null;
    banner.hidden = false;
    var first = banner.querySelector('.cc-btn');
    if (fromEl && first) first.focus();
  }

  function init() {
    // GPC always wins: keep analytics denied and record it.
    if (gpc) { update(false); if (read() !== 'denied') { save('denied'); clearGaCookies(); } }
    document.querySelectorAll('[data-cookie-settings]').forEach(function (el) {
      el.addEventListener('click', function (e) { e.preventDefault(); open(el); });
    });
    var stored = read();
    if (!gpc && stored !== 'granted' && stored !== 'denied' && typeof window.gtag === 'function') open(null);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
