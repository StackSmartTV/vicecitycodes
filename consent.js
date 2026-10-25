/* Vice City Codes analytics consent banner (self-hosted).
   Google Consent Mode v2 defaults are set inline in each page <head>:
   EEA/UK/CH deny everything until Google's own consent message (ads) and this
   banner (analytics) update it; elsewhere ads follow the US opt-out model run by
   Google's US state regulations message. This banner controls ONLY
   analytics_storage, never ad_* signals, so it cannot override Google's message.
   GPC is honored as an analytics Reject and an ads opt-out (set in <head>).
   Where Google's TCF message applies (gdprApplies), the banner does not pop up
   on its own, so EEA/UK/CH visitors never see two banners at once; analytics
   simply stays off unless they opt in via "Cookie settings". */
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
    body: 'Usamos Google Analytics para contar visitas solo si lo aceptas. Los anuncios los ofrece Google AdSense y pueden ser personalizados; puedes excluirte con “No vender ni compartir” al pie de la página. Cambia tu elección de analítica cuando quieras con “Configuración de cookies”.',
    gpc: 'Tu navegador envía la señal Global Privacy Control (GPC). La respetamos: las cookies de analítica están desactivadas y pedimos a Google que no personalice anuncios ni use tus datos para publicidad.',
    accept: 'Aceptar', reject: 'Rechazar', ok: 'Entendido', more: 'Más información',
    optedOut: 'Te excluiste de los anuncios personalizados y de la venta o el intercambio de datos en este navegador.',
    optedIn: 'Los anuncios pueden ser personalizados en este navegador, salvo que te excluyas.',
    gpcOn: 'Tu navegador envía Global Privacy Control, así que ya estás excluido.'
  } : {
    label: 'Cookie notice',
    title: 'Cookies & analytics',
    body: 'We use Google Analytics to count visits only if you accept. Ads are served by Google AdSense and may be personalized; you can opt out with “Do Not Sell or Share” in the page footer. Change your analytics choice any time with “Cookie settings”.',
    gpc: 'Your browser sends a Global Privacy Control (GPC) signal. We honor it: analytics cookies stay off, and we ask Google not to personalize ads or use your data for advertising.',
    accept: 'Accept', reject: 'Reject', ok: 'OK', more: 'Learn more',
    optedOut: 'You are opted out of personalized ads and the sale or sharing of your data on this browser.',
    optedIn: 'Ads on this browser may be personalized unless you opt out.',
    gpcOn: 'Your browser sends Global Privacy Control, so you are already opted out.'
  };

  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function update(granted) {
    if (typeof window.gtag !== 'function') return;
    // Analytics only: ad_* signals belong to Google's consent / US state messages.
    window.gtag('consent', 'update', { analytics_storage: granted ? 'granted' : 'denied' });
  }
  function analyticsGranted() { return !gpc && read() === 'granted'; }

  // Ads opt-out ("Do Not Sell or Share") for this browser, on top of Google's own link.
  var ADS_KEY = 'vcc-ads-optout';
  function adsOptedOut() { try { return gpc || localStorage.getItem(ADS_KEY) === '1'; } catch (e) { return gpc; } }
  function setAdsOptOut(on) {
    try { if (on) localStorage.setItem(ADS_KEY, '1'); else localStorage.removeItem(ADS_KEY); } catch (e) {}
    if (on && typeof window.gtag === 'function') {
      window.gtag('consent', 'update', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      window.gtag('set', 'restricted_data_processing', true);
    }
    if (!on) { location.reload(); return; } // re-apply the regional defaults from <head>
    (window.adsbygoogle = window.adsbygoogle || []).requestNonPersonalizedAds = 1;
    renderAdsOptOut();
  }
  function renderAdsOptOut() {
    var out = adsOptedOut();
    document.querySelectorAll('[data-ads-optout-status]').forEach(function (el) {
      el.textContent = gpc ? T.gpcOn : (out ? T.optedOut : T.optedIn);
    });
    document.querySelectorAll('[data-ads-optout]').forEach(function (el) {
      el.hidden = gpc;
      el.setAttribute('aria-pressed', out ? 'true' : 'false');
      var label = out ? el.getAttribute('data-label-on') : el.getAttribute('data-label-off');
      if (label) el.textContent = label;
    });
  }

  // Google's TCF consent message (Privacy & messaging) exposes __tcfapi.
  // gdprApplies is Google's own region decision, so no IP lookup of ours is needed.
  function whenTcf(cb) {
    var waited = 0, done = false;
    function finish(v) { if (!done) { done = true; cb(v); } }
    (function poll() {
      if (typeof window.__tcfapi === 'function') {
        try {
          window.__tcfapi('addEventListener', 2, function (tc, ok) {
            if (!ok || !tc) return;
            if (tc.gdprApplies && (tc.eventStatus === 'tcloaded' || tc.eventStatus === 'useractioncomplete')) {
              // Google's message may update analytics_storage; our banner stays the authority for analytics.
              update(analyticsGranted());
            }
            finish(tc.gdprApplies === true);
          });
        } catch (e) { finish(false); }
        setTimeout(function () { finish(false); }, 3000);
        return;
      }
      waited += 250;
      if (waited >= 3000) finish(false); else setTimeout(poll, 250);
    })();
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
    document.querySelectorAll('[data-ads-optout]').forEach(function (el) {
      el.addEventListener('click', function (e) { e.preventDefault(); setAdsOptOut(!adsOptedOut()); });
    });
    renderAdsOptOut();
    if (typeof window.gtag !== 'function') return;
    var stored = read();
    var ask = !gpc && stored !== 'granted' && stored !== 'denied';
    // Let Google's EU/UK/CH consent message go alone; show our analytics banner everywhere else.
    whenTcf(function (gdprApplies) {
      var now = read();
      if (ask && !gdprApplies && now !== 'granted' && now !== 'denied') open(null);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
