/* Kilowatt Triage — interactions. No dependencies. */
(() => {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const root = document.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fmt = (n, d = 0) => Number(n).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
  const NS = 'http://www.w3.org/2000/svg';
  const svgEl = (name, attrs = {}) => {
    const el = document.createElementNS(NS, name);
    Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
    return el;
  };

  /* ---------- reveal on scroll ---------- */
  const revealIO = 'IntersectionObserver' in window
    ? new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) { e.target.classList.add('in'); revealIO.unobserve(e.target); }
        });
      }, { threshold: 0, rootMargin: '0px 0px -8% 0px' })
    : null;
  $$('[data-reveal], [data-inview]').forEach((el) => {
    if (reduce || !revealIO) el.classList.add('in'); else revealIO.observe(el);
  });

  /* ---------- number counters ---------- */
  function runCount(el) {
    const to = parseFloat(el.dataset.count);
    const d = parseInt(el.dataset.dec || '0', 10);
    if (reduce) { el.textContent = fmt(to, d); return; }
    const t0 = performance.now();
    const dur = 1400;
    const step = (t) => {
      const p = Math.min(1, (t - t0) / dur);
      el.textContent = fmt(to * (1 - Math.pow(1 - p, 4)), d);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
  const counters = $$('[data-count]');
  if ('IntersectionObserver' in window && !reduce) {
    const cIO = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { cIO.unobserve(e.target); runCount(e.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach((el) => { el.textContent = fmt(0, parseInt(el.dataset.dec || '0', 10)); cIO.observe(el); });
  }

  /* ---------- scroll thread + nav state ---------- */
  const thread = $('#thread');
  const navSec = $('#navSec');
  const navPct = $('#navPct');
  const sections = $$('[data-sec]');
  const navLinks = $$('#navList a');
  let ticking = false;

  function update() {
    ticking = false;
    const max = root.scrollHeight - window.innerHeight;
    const p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    if (thread) thread.style.setProperty('--p', p.toFixed(4));
    if (navPct) navPct.textContent = Math.round(p * 100) + '%';
    let cur = sections[0];
    const line = window.innerHeight * 0.4;
    sections.forEach((s) => { if (s.getBoundingClientRect().top <= line) cur = s; });
    if (cur && navSec && navSec.textContent !== cur.dataset.sec) navSec.textContent = cur.dataset.sec;
    navLinks.forEach((a) => {
      const on = cur && a.getAttribute('href') === '#' + cur.id;
      if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
  }
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } };
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  update();

  /* ---------- mobile menu ---------- */
  const menuBtn = $('.nav__btn');
  const closeMenu = () => {
    if (!menuBtn) return;
    menuBtn.setAttribute('aria-expanded', 'false');
    root.classList.remove('menu-open');
  };
  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      const open = menuBtn.getAttribute('aria-expanded') === 'true';
      menuBtn.setAttribute('aria-expanded', String(!open));
      root.classList.toggle('menu-open', !open);
    });
    navLinks.forEach((a) => a.addEventListener('click', closeMenu));
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && root.classList.contains('menu-open')) { closeMenu(); menuBtn.focus(); }
    });
  }

  /* ---------- hero: gentle pointer parallax ---------- */
  const hero = $('.hero');
  if (hero && !reduce && window.matchMedia('(pointer: fine)').matches) {
    hero.addEventListener('pointermove', (e) => {
      const r = hero.getBoundingClientRect();
      hero.style.setProperty('--mx', ((e.clientX - r.left) / r.width - 0.5).toFixed(3));
      hero.style.setProperty('--my', ((e.clientY - r.top) / r.height - 0.5).toFixed(3));
    });
  }

  /* ---------- geometric web generator ---------- */
  // spokes radiate from (cx,cy); rings are drawn as gently sagging threads between spokes.
  function buildWeb(svg, o) {
    const { cx, cy, R, spokes, rings, a0 = 0, a1 = Math.PI * 2, closed = true, sag = 0.84 } = o;
    const n = closed ? spokes : spokes - 1;
    const ang = (k) => a0 + (k * (a1 - a0)) / n;
    const pt = (r, a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    let d = '';
    for (let k = 0; k < spokes; k++) {
      const [x, y] = pt(R, ang(k));
      d += `M${cx.toFixed(1)} ${cy.toFixed(1)}L${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    for (let j = 1; j <= rings; j++) {
      const r = (R * j) / rings;
      for (let k = 0; k < n; k++) {
        const a = ang(k), b = ang(k + 1), m = (a + b) / 2;
        const half = Math.abs(b - a) / 2;
        const [x1, y1] = pt(r, a);
        const [x2, y2] = pt(r, b);
        const [qx, qy] = pt((r * Math.cos(half)) * sag, m);
        d += `M${x1.toFixed(1)} ${y1.toFixed(1)}Q${qx.toFixed(1)} ${qy.toFixed(1)} ${x2.toFixed(1)} ${y2.toFixed(1)}`;
      }
    }
    svg.appendChild(svgEl('path', { d, class: 'w-line' }));
  }

  /* ---------- footer corner web ---------- */
  const corner = $('#cornerWeb');
  if (corner) buildWeb(corner, { cx: 0, cy: 0, R: 190, spokes: 7, rings: 6, a0: 0, a1: Math.PI / 2, closed: false, sag: 0.8 });

  /* ---------- approach: four-stage web ---------- */
  const STAGES = [
    { name: 'Describe', text: 'Capture the building, its characteristics, its climate zone and its existing heating system.', list: ['Building characteristics', 'Climate zone', 'Existing heating system'], x: 110, y: 440 },
    { name: 'Compare', text: 'Examine the retrofit interventions that could apply to that building.', list: ['Insulation', 'Efficient lighting, including LED', 'Boiler efficiency', 'Heating-system and fuel-switch options'], x: 235, y: 200 },
    { name: 'Evaluate', text: 'Weigh each option against what it could save, what it costs, whether it is feasible, and how it fits with the others.', list: ['Potential energy savings', 'Initial investment cost', 'Technical feasibility', 'Compatibility between interventions'], x: 400, y: 410 },
    { name: 'Prioritize', text: 'Identify the promising next steps under a limited budget, with the reasoning visible.', list: ['Promising measures first', 'Under budget constraints', 'Transparent, explainable logic'], x: 500, y: 130 },
  ];
  const web = $('#web');
  const stageBtns = $$('.stage');
  const nodeEls = [];

  if (web) {
    buildWeb(web, { cx: 300, cy: 300, R: 285, spokes: 14, rings: 7, sag: 0.86 });
    web.appendChild(svgEl('path', {
      d: STAGES.map((s, i) => `${i ? 'L' : 'M'}${s.x} ${s.y}`).join(''),
      class: 'w-path', pathLength: '1',
    }));
    STAGES.forEach((s, i) => {
      const g = svgEl('g', { class: 'w-node', transform: `translate(${s.x} ${s.y})` });
      g.appendChild(svgEl('circle', { class: 'w-ring', r: 24, fill: 'none' }));
      g.appendChild(svgEl('circle', { class: 'c', r: 13 }));
      const num = svgEl('text', { class: 'num' });
      num.textContent = String(i + 1);
      g.appendChild(num);
      const label = svgEl('text', { x: i % 2 ? 22 : -22, y: i % 2 ? -18 : 28, 'text-anchor': i % 2 ? 'start' : 'end' });
      label.textContent = s.name;
      g.appendChild(label);
      g.addEventListener('click', () => setStage(i));
      web.appendChild(g);
      nodeEls.push(g);
    });
  }

  function setStage(i) {
    const s = STAGES[i];
    stageBtns.forEach((b, k) => b.setAttribute('aria-pressed', String(k === i)));
    nodeEls.forEach((g, k) => g.classList.toggle('is-active', k === i));
    $('#spK').textContent = `Stage 0${i + 1} / 04`;
    $('#spT').textContent = s.name;
    $('#spD').textContent = s.text;
    const ul = $('#spL');
    ul.textContent = '';
    s.list.forEach((t) => { const li = document.createElement('li'); li.textContent = t; ul.appendChild(li); });
  }
  stageBtns.forEach((b, i) => {
    b.addEventListener('click', () => setStage(i));
    b.addEventListener('mouseenter', () => { if (window.matchMedia('(hover: hover)').matches) setStage(i); });
  });
  if (stageBtns.length) setStage(0);

  /* ---------- evidence: climate zones ---------- */
  const AREA = 4000;
  const MAX_INTENSITY = 250;
  const zrows = $$('.zbar');
  const zbtns = $$('[data-zone]', $('.zone-tabs') || document);

  zrows.forEach((r) => {
    r.style.setProperty('--w-h', (parseFloat(r.dataset.h) / MAX_INTENSITY * 100) + '%');
    r.style.setProperty('--w-l', (parseFloat(r.dataset.l) / MAX_INTENSITY * 100) + '%');
    r.style.setProperty('--w-e', (parseFloat(r.dataset.e) / MAX_INTENSITY * 100) + '%');
  });

  function setZone(z) {
    const r = zrows.find((x) => x.dataset.zone === String(z));
    if (!r) return;
    zrows.forEach((x) => x.classList.toggle('is-on', x === r));
    zbtns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.zone === String(z))));
    const h = parseFloat(r.dataset.h), l = parseFloat(r.dataset.l), e = parseFloat(r.dataset.e), t = parseFloat(r.dataset.t);
    $('#zdName').textContent = 'Zone ' + z;
    $('#zdH').textContent = fmt(h, 2);
    $('#zdL').textContent = fmt(l, 2);
    $('#zdE').textContent = fmt(e, 2);
    $('#zdT').textContent = fmt(t, 2);
    $('#zdAbs').textContent = fmt(Math.round(t * AREA)) + ' kWh/yr';
  }
  zbtns.forEach((b) => b.addEventListener('click', () => setZone(b.dataset.zone)));
  zrows.forEach((r) => r.addEventListener('click', () => setZone(r.dataset.zone)));
  setZone(3);

  /* ---------- evidence: interventions ---------- */
  const ivList = $('#ivs');
  const ivs = ivList ? $$('.iv', ivList) : [];
  const MAX_SAVE = 450000;
  const MAX_COST = 60000;
  ivs.forEach((li) => {
    li.style.setProperty('--s', (parseFloat(li.dataset.save) / MAX_SAVE * 100) + '%');
    li.style.setProperty('--c', (parseFloat(li.dataset.cost) / MAX_COST * 100) + '%');
  });
  // bar widths read the CSS vars from the list, so mirror them onto it per row via inheritance
  ivs.forEach((li) => {
    $$('.bar__s', li).forEach((b) => { b.style.setProperty('--s', li.style.getPropertyValue('--s')); });
    $$('.bar__c', li).forEach((b) => { b.style.setProperty('--c', li.style.getPropertyValue('--c')); });
  });

  const SORTS = {
    order: { fn: (a, b) => a.dataset.order - b.dataset.order, msg: 'Shown in the order the report lists them.' },
    save: { fn: (a, b) => b.dataset.save - a.dataset.save, msg: 'Sorted by reported savings, highest first.' },
    cost: { fn: (a, b) => a.dataset.cost - b.dataset.cost, msg: 'Sorted by estimated investment, lowest first.' },
  };
  function sortBy(key) {
    const sorted = [...ivs].sort(SORTS[key].fn);
    const first = new Map(ivs.map((el) => [el, el.getBoundingClientRect().top]));
    sorted.forEach((el) => ivList.appendChild(el));
    if (!reduce && el_animate()) {
      sorted.forEach((el) => {
        const dy = first.get(el) - el.getBoundingClientRect().top;
        if (dy) el.animate([{ transform: `translateY(${dy}px)` }, { transform: 'none' }], { duration: 520, easing: 'cubic-bezier(.2,.7,.1,1)' });
      });
    }
    $$('[data-sort]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.sort === key)));
    const note = $('#sortNote');
    if (note) note.textContent = SORTS[key].msg;
  }
  function el_animate() { return typeof Element !== 'undefined' && typeof Element.prototype.animate === 'function'; }
  $$('[data-sort]').forEach((b) => b.addEventListener('click', () => sortBy(b.dataset.sort)));

  /* ---------- progress summary (kept in sync with the markup) ---------- */
  const sum = $('#pSum');
  if (sum) {
    const done = $$('.step.is-done').length, now = $$('.step.is-now').length, next = $$('.step.is-next').length;
    sum.textContent = `${done} complete · ${now} in progress · ${next} planned`;
  }
})();
