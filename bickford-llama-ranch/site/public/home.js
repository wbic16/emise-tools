'use strict';
/* Public homepage: renders the 5 CMS scrolls from ranch.phext via SQ select.
   Read-only. In production nginx proxies only select/toc/version GETs here,
   with the SQ key added server-side — this file contains no key. */
const API = new URLSearchParams(location.search).get('api') || '/api/v2';
const P = 'ranch';
const FIELDS = { // coordinate -> element id (CMS map: 1.1.1/1.1.1/1.1.F)
  1: 'cms-title', 2: 'cms-tagline', 3: 'cms-announce', 4: 'cms-about', 5: 'cms-contact'
};
(async () => {
  for (const [f, id] of Object.entries(FIELDS)) {
    try {
      const txt = (await (await fetch(`${API}/select?p=${P}&c=1.1.1/1.1.1/1.1.${f}`)).text()).trim();
      const el = document.getElementById(id);
      if (txt) { el.textContent = txt; el.hidden = false; }
    } catch (e) { /* leave the static fallback in place */ }
  }
})();
