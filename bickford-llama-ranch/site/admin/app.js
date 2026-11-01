'use strict';
/* Bickford Llama Ranch admin.
   Data model: NO JSON storage. ranch.phext is the database; every field is
   its own scroll at its own coordinate (see README.md for the map).
   An edit = ONE POST /api/v2/update?p=ranch&c=<coord> with the raw value.
   SQ's json-export is used only to *discover* coordinates on load. */
const P = 'ranch';
const API = new URLSearchParams(location.search).get('api') || '/api/v2';
let DB = new Map(); // coord -> plain text value (in-memory copy only)

const profC = (a, f) => `2.1.${a}/1.1.1/1.1.${f}`;
const bredC = (a, b, f) => `2.1.${a}/1.1.2/${b}.1.${f}`;
const vaccC = (a, v, f) => `2.1.${a}/1.1.3/${v}.1.${f}`;
const cmsC  = f => `1.1.1/1.1.1/1.1.${f}`;
const setC  = f => `1.1.1/1.1.2/1.1.${f}`;

const PROF = ['name','sex','birth date','sire','dam','color/markings','status','notes'];
const CMS  = ['Site title','Tagline','Announcement','About text','Contact line'];
const SETS = ['Reminder email recipients (comma-separated)','Ranch name / branding line'];

const get = c => (DB.get(c) || '').trim();
const status = msg => { document.getElementById('save-status').textContent = msg; };

async function save(coord, value) {
  status(`Saving ${coord} …`);
  const r = await fetch(`${API}/update?p=${P}&c=${coord}`, { method: 'POST', body: value });
  if (!r.ok) { status(`SAVE FAILED at ${coord} (HTTP ${r.status})`); throw new Error(r.status); }
  DB.set(coord, value);
  status(`Saved ${coord} — ${await r.text()}`);
}

async function load() {
  const rows = await (await fetch(`${API}/json-export?p=${P}`)).json();
  DB = new Map(rows.map(r => [r.coord, r.scroll]));
  render();
}

/* ---- discovery: ids present in the phext ---- */
function animalIds() {
  const s = new Set();
  for (const c of DB.keys()) { const m = c.match(/^2\.1\.(\d+)\//); if (m) s.add(+m[1]); }
  return [...s].sort((a, b) => a - b);
}
function recordIds(a, book) { // book 2 = breedings, 3 = vaccinations
  const s = new Set(), re = new RegExp(`^2\\.1\\.${a}/1\\.1\\.${book}/(\\d+)\\.1\\.`);
  for (const c of DB.keys()) { const m = c.match(re); if (m) s.add(+m[1]); }
  return [...s].sort((a, b) => a - b);
}
const nextId = ids => (ids.length ? Math.max(...ids) + 1 : 1);

/* ---- dates ---- */
const DAY = 864e5;
const parseD = s => { const d = new Date(s + 'T12:00:00'); return isNaN(d) ? null : d; };
const addD = (d, n) => new Date(d.getTime() + n * DAY);
const fmtD = d => d.toISOString().slice(0, 10);
const today = () => { const d = new Date(); d.setHours(12, 0, 0, 0); return d; };

/* Due items: {date, text, kind} — mirrors reminders/remind.py */
function dueItems() {
  const out = [], now = today();
  for (const a of animalIds()) {
    const name = get(profC(a, 1)) || `Animal ${a}`;
    for (const b of recordIds(a, 2)) {
      const bred = parseD(get(bredC(a, b, 1)));
      if (!bred) continue;
      const outcome = get(bredC(a, b, 6)) || 'unknown';
      [[14, 3], [21, 4], [45, 5]].forEach(([days, f]) => {
        if (!get(bredC(a, b, f))) {
          const due = addD(bred, days);
          if (due <= addD(now, 14)) out.push({ date: due, kind: 'spit-off',
            text: `${name}: spit-off check (${days}d) due ${fmtD(due)} — bred ${fmtD(bred)}` });
        }
      });
      if ((outcome === 'pregnant' || outcome === 'unknown') && !get(bredC(a, b, 7))) {
        const due = addD(bred, 342), lo = addD(bred, 332), hi = addD(bred, 352);
        if (now >= addD(due, -30)) out.push({ date: due, kind: 'cria',
          text: `${name}: cria due around ${fmtD(due)} (window ${fmtD(lo)}–${fmtD(hi)})` });
        if (outcome === 'pregnant') { // dashboard-only note: dam CD/T booster window
          const w0 = addD(due, -42), w1 = addD(due, -28);
          const covered = recordIds(a, 3).some(v =>
            /cd\/?t/i.test(get(vaccC(a, v, 2))) && (d => d && d >= w0 && d <= w1)(parseD(get(vaccC(a, v, 1)))));
          if (!covered && now <= w1) out.push({ date: w0, kind: 'booster-note',
            text: `${name}: CD/T pre-birthing booster window ${fmtD(w0)}–${fmtD(w1)} (Merck: 4–6 weeks before due)` });
        }
      }
    }
    const latest = {}; // vaccine name -> latest event
    for (const v of recordIds(a, 3)) {
      const key = (get(vaccC(a, v, 2)) || 'vaccine').toLowerCase();
      if (!latest[key] || get(vaccC(a, v, 1)) > get(vaccC(a, latest[key], 1))) latest[key] = v;
    }
    for (const key of Object.keys(latest)) {
      const v = latest[key], given = parseD(get(vaccC(a, v, 1))), interval = +get(vaccC(a, v, 3));
      if (!given || !interval) continue;
      const due = addD(given, interval);
      if (due <= addD(now, 60)) out.push({ date: due, kind: 'vaccination',
        text: `${name}: ${get(vaccC(a, v, 2))} next due ${fmtD(due)} (given ${fmtD(given)}, every ${interval}d)` });
    }
  }
  return out.sort((x, y) => x.date - y.date);
}

/* ---- rendering ---- */
function editable(coord, value, opts = {}) {
  const el = document.createElement(opts.long ? 'textarea' : 'input');
  el.value = value; el.dataset.coord = coord;
  if (opts.type) el.type = opts.type;
  el.addEventListener('change', async () => { await save(coord, el.value); renderDue(); });
  return el;
}
function render() {
  const now = today();
  renderDue();
  // Herd: one block per animal, profile fields + its records
  const herd = document.getElementById('herd'); herd.innerHTML = '';
  for (const a of animalIds()) {
    const det = document.createElement('details');
    const sum = document.createElement('summary');
    sum.textContent = `#${a} ${get(profC(a, 1)) || '(unnamed)'} — ${get(profC(a, 2))}, status ${get(profC(a, 7)) || 'active'}`;
    det.appendChild(sum);
    const grid = document.createElement('div'); grid.className = 'grid';
    PROF.forEach((label, i) => {
      const wrap = document.createElement('div'); wrap.className = 'field';
      const lab = document.createElement('label'); lab.textContent = label + ' ';
      lab.appendChild(editable(profC(a, i + 1), get(profC(a, i + 1)), { type: i === 2 ? 'date' : '', long: i === 7 }));
      wrap.appendChild(lab); grid.appendChild(wrap);
    });
    det.appendChild(grid);
    det.appendChild(recordTable(a, 2, 'Breedings',
      ['date','sire','spit-off 14d','spit-off 21d','spit-off 45d','outcome','cria birth','cria note'], bredC));
    det.appendChild(recordTable(a, 3, 'Vaccinations',
      ['date given','vaccine','interval days','notes'], vaccC));
    herd.appendChild(det);
  }
  document.querySelectorAll('.animal-picker').forEach(sel => {
    sel.innerHTML = animalIds().map(a =>
      `<option value="${a}">#${a} ${get(profC(a, 1))}</option>`).join('');
  });
  fillFields('cms', CMS, cmsC); fillFields('settings', SETS, setC);
  status(`Loaded ${DB.size} scrolls from ranch.phext`);
}
function recordTable(a, book, title, labels, coordFn) {
  const wrap = document.createElement('div');
  const h = document.createElement('h4'); h.textContent = title; wrap.appendChild(h);
  const t = document.createElement('table');
  t.innerHTML = '<tr>' + labels.map(l => `<th>${l}</th>`).join('') + '</tr>';
  for (const r of recordIds(a, book)) {
    const tr = document.createElement('tr');
    labels.forEach((_, i) => {
      const td = document.createElement('td');
      td.appendChild(editable(coordFn(a, r, i + 1), get(coordFn(a, r, i + 1)),
        { type: i === 0 ? 'date' : '' }));
      tr.appendChild(td);
    });
    t.appendChild(tr);
  }
  wrap.appendChild(t); return wrap;
}
function fillFields(id, labels, coordFn) {
  const box = document.getElementById(id); box.innerHTML = '';
  labels.forEach((label, i) => {
    const wrap = document.createElement('div'); wrap.className = 'field';
    const lab = document.createElement('label'); lab.textContent = label + ' ';
    lab.appendChild(editable(coordFn(i + 1), get(coordFn(i + 1)), { long: i >= 2 }));
    wrap.appendChild(lab); box.appendChild(wrap);
  });
}
function renderDue() {
  const now = today(), ul = document.getElementById('due-list'); ul.innerHTML = '';
  const items = dueItems();
  if (!items.length) { ul.innerHTML = '<li>Nothing due.</li>'; return; }
  for (const it of items) {
    const li = document.createElement('li');
    li.textContent = it.text;
    li.className = it.date < now ? 'due-overdue' : (it.date <= addD(now, 14) ? 'due-soon' : 'due-ok');
    ul.appendChild(li);
  }
}

/* ---- add forms: write only the new record's scrolls, one POST per field ---- */
async function writeRecord(pairs) { for (const [c, v] of pairs) if (v !== '') await save(c, v); }
document.getElementById('add-animal').addEventListener('submit', async e => {
  e.preventDefault(); const f = new FormData(e.target), a = nextId(animalIds());
  await writeRecord([[profC(a,1),f.get('name')],[profC(a,2),f.get('sex')],[profC(a,3),f.get('birth')],
    [profC(a,4),f.get('sire')],[profC(a,5),f.get('dam')],[profC(a,6),f.get('color')],[profC(a,7),'active']]);
  e.target.reset(); render();
});
document.getElementById('add-breeding').addEventListener('submit', async e => {
  e.preventDefault(); const f = new FormData(e.target), a = +f.get('animal'), b = nextId(recordIds(a, 2));
  await writeRecord([[bredC(a,b,1),f.get('date')],[bredC(a,b,2),f.get('sire')],[bredC(a,b,6),f.get('outcome')]]);
  e.target.reset(); render();
});
document.getElementById('add-vaccination').addEventListener('submit', async e => {
  e.preventDefault(); const f = new FormData(e.target), a = +f.get('animal'), v = nextId(recordIds(a, 3));
  await writeRecord([[vaccC(a,v,1),f.get('date')],[vaccC(a,v,2),f.get('vaccine')],
    [vaccC(a,v,3),f.get('interval')],[vaccC(a,v,4),f.get('notes')]]);
  e.target.reset(); render();
});

load().catch(err => status('Could not reach SQ at ' + API + ' — is `sq host` running? ' + err));
