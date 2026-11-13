/* Kilowatt Triage — interactions + school assessment. No dependencies. */
(() => {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const root = document.documentElement;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fmt = (n, d = 0) => Number(n).toLocaleString('en-US', {
    minimumFractionDigits: d,
    maximumFractionDigits: d
  });
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
          if (e.isIntersecting) {
            e.target.classList.add('in');
            revealIO.unobserve(e.target);
          }
        });
      }, { threshold: 0, rootMargin: '0px 0px -8% 0px' })
    : null;

  $$('[data-reveal], [data-inview]').forEach((el) => {
    if (reduce || !revealIO) el.classList.add('in');
    else revealIO.observe(el);
  });

  /* ---------- number counters ---------- */
  function runCount(el) {
    const to = parseFloat(el.dataset.count);
    const d = parseInt(el.dataset.dec || '0', 10);

    if (reduce) {
      el.textContent = fmt(to, d);
      return;
    }

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
        if (e.isIntersecting) {
          cIO.unobserve(e.target);
          runCount(e.target);
        }
      });
    }, { threshold: 0.4 });

    counters.forEach((el) => {
      el.textContent = fmt(0, parseInt(el.dataset.dec || '0', 10));
      cIO.observe(el);
    });
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
    const p = max > 0
      ? Math.min(1, Math.max(0, window.scrollY / max))
      : 0;

    if (thread) thread.style.setProperty('--p', p.toFixed(4));
    if (navPct) navPct.textContent = Math.round(p * 100) + '%';

    let cur = sections[0];
    const line = window.innerHeight * 0.4;

    sections.forEach((s) => {
      if (s.getBoundingClientRect().top <= line) cur = s;
    });

    if (cur && navSec && navSec.textContent !== cur.dataset.sec) {
      navSec.textContent = cur.dataset.sec;
    }

    navLinks.forEach((a) => {
      const on = cur && a.getAttribute('href') === '#' + cur.id;
      if (on) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
  }

  const onScroll = () => {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  };

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
      if (e.key === 'Escape' && root.classList.contains('menu-open')) {
        closeMenu();
        menuBtn.focus();
      }
    });
  }

  /* ---------- hero: gentle pointer parallax ---------- */
  const hero = $('.hero');

  if (hero && !reduce && window.matchMedia('(pointer: fine)').matches) {
    hero.addEventListener('pointermove', (e) => {
      const r = hero.getBoundingClientRect();

      hero.style.setProperty(
        '--mx',
        ((e.clientX - r.left) / r.width - 0.5).toFixed(3)
      );

      hero.style.setProperty(
        '--my',
        ((e.clientY - r.top) / r.height - 0.5).toFixed(3)
      );
    });
  }

  /* ---------- geometric web generator ---------- */
  function buildWeb(svg, o) {
    const {
      cx, cy, R, spokes, rings,
      a0 = 0,
      a1 = Math.PI * 2,
      closed = true,
      sag = 0.84
    } = o;

    const n = closed ? spokes : spokes - 1;
    const ang = (k) => a0 + (k * (a1 - a0)) / n;
    const pt = (r, a) => [
      cx + r * Math.cos(a),
      cy + r * Math.sin(a)
    ];

    let d = '';

    for (let k = 0; k < spokes; k++) {
      const [x, y] = pt(R, ang(k));
      d += `M${cx.toFixed(1)} ${cy.toFixed(1)}L${x.toFixed(1)} ${y.toFixed(1)}`;
    }

    for (let j = 1; j <= rings; j++) {
      const r = (R * j) / rings;

      for (let k = 0; k < n; k++) {
        const a = ang(k);
        const b = ang(k + 1);
        const m = (a + b) / 2;
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

  if (corner) {
    buildWeb(corner, {
      cx: 0,
      cy: 0,
      R: 190,
      spokes: 7,
      rings: 6,
      a0: 0,
      a1: Math.PI / 2,
      closed: false,
      sag: 0.8
    });
  }

  /* ---------- approach: four-stage web ---------- */
  const STAGES = [
    {
      name: 'Describe',
      text: 'Capture the building, its characteristics, its climate zone and its existing heating system.',
      list: ['Building characteristics', 'Climate zone', 'Existing heating system'],
      x: 110,
      y: 440
    },
    {
      name: 'Compare',
      text: 'Examine the retrofit interventions that could apply to that building.',
      list: [
        'Insulation',
        'Efficient lighting, including LED',
        'Boiler efficiency',
        'Heating-system and fuel-switch options'
      ],
      x: 235,
      y: 200
    },
    {
      name: 'Evaluate',
      text: 'Weigh each option against what it could save, what it costs, whether it is feasible, and how it fits with the others.',
      list: [
        'Potential energy savings',
        'Initial investment cost',
        'Technical feasibility',
        'Compatibility between interventions'
      ],
      x: 400,
      y: 410
    },
    {
      name: 'Prioritize',
      text: 'Identify the promising next steps under a limited budget, with the reasoning visible.',
      list: [
        'Promising measures first',
        'Under budget constraints',
        'Transparent, explainable logic'
      ],
      x: 500,
      y: 130
    }
  ];

  const web = $('#web');
  const stageBtns = $$('.stage');
  const nodeEls = [];

  if (web) {
    buildWeb(web, {
      cx: 300,
      cy: 300,
      R: 285,
      spokes: 14,
      rings: 7,
      sag: 0.86
    });

    web.appendChild(svgEl('path', {
      d: STAGES.map((s, i) => `${i ? 'L' : 'M'}${s.x} ${s.y}`).join(''),
      class: 'w-path',
      pathLength: '1'
    }));

    STAGES.forEach((s, i) => {
      const g = svgEl('g', {
        class: 'w-node',
        transform: `translate(${s.x} ${s.y})`
      });

      g.appendChild(svgEl('circle', {
        class: 'w-ring',
        r: 24,
        fill: 'none'
      }));

      g.appendChild(svgEl('circle', { class: 'c', r: 13 }));

      const num = svgEl('text', { class: 'num' });
      num.textContent = String(i + 1);
      g.appendChild(num);

      const label = svgEl('text', {
        x: i % 2 ? 22 : -22,
        y: i % 2 ? -18 : 28,
        'text-anchor': i % 2 ? 'start' : 'end'
      });

      label.textContent = s.name;
      g.appendChild(label);

      g.addEventListener('click', () => setStage(i));
      web.appendChild(g);
      nodeEls.push(g);
    });
  }

  function setStage(i) {
    const s = STAGES[i];

    stageBtns.forEach((b, k) => {
      b.setAttribute('aria-pressed', String(k === i));
    });

    nodeEls.forEach((g, k) => {
      g.classList.toggle('is-active', k === i);
    });

    const stageKey = $('#spK');
    const stageTitle = $('#spT');
    const stageDescription = $('#spD');
    const ul = $('#spL');

    if (stageKey) stageKey.textContent = `Stage 0${i + 1} / 04`;
    if (stageTitle) stageTitle.textContent = s.name;
    if (stageDescription) stageDescription.textContent = s.text;

    if (ul) {
      ul.textContent = '';

      s.list.forEach((t) => {
        const li = document.createElement('li');
        li.textContent = t;
        ul.appendChild(li);
      });
    }
  }

  stageBtns.forEach((b, i) => {
    b.addEventListener('click', () => setStage(i));

    b.addEventListener('mouseenter', () => {
      if (window.matchMedia('(hover: hover)').matches) setStage(i);
    });
  });

  if (stageBtns.length) setStage(0);

  /* ---------- evidence: climate zones ---------- */
  const AREA = 4000;
  const MAX_INTENSITY = 250;
  const zrows = $$('.zbar');
  const zbtns = $$('[data-zone]', $('.zone-tabs') || document);

  zrows.forEach((r) => {
    r.style.setProperty(
      '--w-h',
      (parseFloat(r.dataset.h) / MAX_INTENSITY * 100) + '%'
    );

    r.style.setProperty(
      '--w-l',
      (parseFloat(r.dataset.l) / MAX_INTENSITY * 100) + '%'
    );

    r.style.setProperty(
      '--w-e',
      (parseFloat(r.dataset.e) / MAX_INTENSITY * 100) + '%'
    );
  });

  function setZone(z) {
    const r = zrows.find((x) => x.dataset.zone === String(z));
    if (!r) return;

    zrows.forEach((x) => x.classList.toggle('is-on', x === r));

    zbtns.forEach((b) => {
      b.setAttribute('aria-pressed', String(b.dataset.zone === String(z)));
    });

    const h = parseFloat(r.dataset.h);
    const l = parseFloat(r.dataset.l);
    const e = parseFloat(r.dataset.e);
    const t = parseFloat(r.dataset.t);

    const zdName = $('#zdName');
    const zdH = $('#zdH');
    const zdL = $('#zdL');
    const zdE = $('#zdE');
    const zdT = $('#zdT');
    const zdAbs = $('#zdAbs');

    if (zdName) zdName.textContent = 'Zone ' + z;
    if (zdH) zdH.textContent = fmt(h, 2);
    if (zdL) zdL.textContent = fmt(l, 2);
    if (zdE) zdE.textContent = fmt(e, 2);
    if (zdT) zdT.textContent = fmt(t, 2);
    if (zdAbs) zdAbs.textContent = fmt(Math.round(t * AREA)) + ' kWh/yr';
  }

  zbtns.forEach((b) => {
    b.addEventListener('click', () => setZone(b.dataset.zone));
  });

  zrows.forEach((r) => {
    r.addEventListener('click', () => setZone(r.dataset.zone));
  });

  setZone(3);

  /* ---------- evidence: interventions ---------- */
  const ivList = $('#ivs');
  const ivs = ivList ? $$('.iv', ivList) : [];
  const MAX_SAVE = 450000;
  const MAX_COST = 60000;

  ivs.forEach((li) => {
    li.style.setProperty(
      '--s',
      (parseFloat(li.dataset.save) / MAX_SAVE * 100) + '%'
    );

    li.style.setProperty(
      '--c',
      (parseFloat(li.dataset.cost) / MAX_COST * 100) + '%'
    );
  });

  ivs.forEach((li) => {
    $$('.bar__s', li).forEach((b) => {
      b.style.setProperty('--s', li.style.getPropertyValue('--s'));
    });

    $$('.bar__c', li).forEach((b) => {
      b.style.setProperty('--c', li.style.getPropertyValue('--c'));
    });
  });

  const SORTS = {
    order: {
      fn: (a, b) => a.dataset.order - b.dataset.order,
      msg: 'Shown in the order the report lists them.'
    },
    save: {
      fn: (a, b) => b.dataset.save - a.dataset.save,
      msg: 'Sorted by reported savings, highest first.'
    },
    cost: {
      fn: (a, b) => a.dataset.cost - b.dataset.cost,
      msg: 'Sorted by estimated investment, lowest first.'
    }
  };

  function sortBy(key) {
    const sorted = [...ivs].sort(SORTS[key].fn);
    const first = new Map(
      ivs.map((el) => [el, el.getBoundingClientRect().top])
    );

    sorted.forEach((el) => ivList.appendChild(el));

    if (!reduce && el_animate()) {
      sorted.forEach((el) => {
        const dy = first.get(el) - el.getBoundingClientRect().top;

        if (dy) {
          el.animate(
            [
              { transform: `translateY(${dy}px)` },
              { transform: 'none' }
            ],
            {
              duration: 520,
              easing: 'cubic-bezier(.2,.7,.1,1)'
            }
          );
        }
      });
    }

    $$('[data-sort]').forEach((b) => {
      b.setAttribute('aria-pressed', String(b.dataset.sort === key));
    });

    const note = $('#sortNote');
    if (note) note.textContent = SORTS[key].msg;
  }

  function el_animate() {
    return typeof Element !== 'undefined' &&
      typeof Element.prototype.animate === 'function';
  }

  $$('[data-sort]').forEach((b) => {
    b.addEventListener('click', () => sortBy(b.dataset.sort));
  });

  /* ---------- progress summary ---------- */
  const sum = $('#pSum');

  if (sum) {
    const done = $$('.step.is-done').length;
    const now = $$('.step.is-now').length;
    const next = $$('.step.is-next').length;

    sum.textContent = `${done} complete · ${now} in progress · ${next} planned`;
  }

  /* ---------- school assessment: Python API ---------- */
  const assessmentForm = $('#assessmentForm');
  const assessmentStatus = $('#assessmentStatus');
  const assessmentSubmit = $('#assessmentSubmit');
  const assessmentResults = $('#assessmentResults');

  if (assessmentForm) {
    const readNumber = (value) => {
      if (value === '' || value === null) return null;
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : null;
    };

    /* ----- results rendering: readable layout instead of a raw dump ----- */

    const LABELS = {
      heating: {
        coal: 'Coal',
        gas: 'Gas',
        district: 'District heating',
        electric: 'Electric',
        other: 'Other',
        unknown: 'Unknown'
      },
      condition: {
        good: 'Good',
        fair: 'Fair',
        poor: 'Poor',
        unknown: 'Unknown'
      },
      fuel: {
        coal: 'Coal',
        natural_gas: 'Natural gas',
        electricity: 'Electricity',
        other: 'Other'
      },
      basis: {
        thermal: 'Thermal (heat)',
        electrical: 'Electrical',
        fuel_switch_unresolved: 'Fuel switch (net effect unverified)'
      },
      compat: {
        compatible: ['Compatible', 'ok'],
        incompatible: ['Incompatible', 'no'],
        needs_review: ['Needs review', 'review']
      }
    };

    const label = (map, key) =>
      (key !== null && key !== undefined && map[key]) || String(key ?? 'Unknown');

    const make = (tag, cls, text) => {
      const node = document.createElement(tag);
      if (cls) node.className = cls;
      if (text !== undefined && text !== null) node.textContent = text;
      return node;
    };

    const kwh = (n) => (Number.isFinite(n) ? `${fmt(n)} kWh` : 'Not available');
    const usd = (n) => (Number.isFinite(n) ? `$${fmt(n)}` : 'Not available');

    function buildTable(caption, headers) {
      const wrap = make('div', 'kt-scroll');
      const table = make('table', 'kt-table');
      table.appendChild(make('caption', 'sr', caption));

      const headRow = make('tr');
      headers.forEach((h) => headRow.appendChild(make('th', null, h)));
      table.appendChild(make('thead')).appendChild(headRow);

      const body = make('tbody');
      table.appendChild(body);
      wrap.appendChild(table);

      return { wrap, body };
    }

    function addRow(body, cells) {
      const row = make('tr');

      cells.forEach((cell) => {
        const td = make('td');

        if (cell instanceof Node) td.appendChild(cell);
        else td.textContent = cell;

        row.appendChild(td);
      });

      body.appendChild(row);
    }

    function renderSummary(target, profile, budget) {
      if (!target) return;
      target.textContent = '';

      const fuels = profile.available_fuels.length
        ? profile.available_fuels.map((f) => label(LABELS.fuel, f)).join(', ')
        : 'None listed';

      const items = [
        ['Climate zone', `Zone ${profile.climate_zone}`],
        ['Floor area', `${fmt(profile.floor_area_m2)} m²`],
        ['Heating system', label(LABELS.heating, profile.heating_system)],
        ['Heating condition', label(LABELS.condition, profile.heating_condition)],
        ['Available fuels', fuels],
        [
          'Electrical capacity',
          profile.electrical_capacity_kw === null
            ? 'Not provided'
            : `${fmt(profile.electrical_capacity_kw, 2)} kW`
        ],
        ['Budget (2021 USD)', usd(budget)]
      ];

      const dl = make('dl', 'kt-summary');

      items.forEach(([term, value]) => {
        const box = make('div');
        box.append(make('dt', null, term), make('dd', null, value));
        dl.appendChild(box);
      });

      target.appendChild(dl);
    }

    function renderMeasures(target, items) {
      if (!target) return;
      target.textContent = '';

      if (!Array.isArray(items) || items.length === 0) {
        target.textContent = 'No interventions were returned.';
        return;
      }

      const { wrap, body } = buildTable(
        'Retrofit interventions evaluated for this school',
        [
          'Measure',
          'Status',
          'Energy type',
          'Estimated saving (kWh/yr)',
          'Reference cost (2021 USD)',
          'Notes'
        ]
      );

      items.forEach((item) => {
        const [statusText, statusKind] =
          LABELS.compat[item.compatibility] || [String(item.compatibility), 'no'];

        const status = make('span', `kt-tag kt-tag--${statusKind}`, statusText);

        const saving = make('div', 'kt-num');

        if (
          item.estimate_status === 'estimated' &&
          Number.isFinite(item.estimated_energy_saving_kwh)
        ) {
          saving.appendChild(
            make('strong', null, fmt(item.estimated_energy_saving_kwh))
          );
        } else if (item.estimate_status === 'not_applicable') {
          saving.appendChild(make('span', 'kt-muted', 'Not applicable'));
        } else {
          saving.appendChild(make('span', 'kt-muted', 'Not calculated'));
        }

        if (Number.isFinite(item.reported_energy_saving_kwh)) {
          saving.appendChild(
            make(
              'div',
              'kt-sub',
              `Reference school: ${fmt(item.reported_energy_saving_kwh)} kWh`
            )
          );
        }

        const notes = make('div');
        if (item.compatibility_reason) {
          notes.appendChild(make('div', null, item.compatibility_reason));
        }
        if (item.estimate_limitation) {
          notes.appendChild(make('div', 'kt-sub', item.estimate_limitation));
        }

        addRow(body, [
          make('span', 'kt-name', item.intervention),
          status,
          label(LABELS.basis, item.reported_saving_basis),
          saving,
          usd(item.investment_cost_usd),
          notes
        ]);
      });

      target.appendChild(wrap);

      target.appendChild(
        make(
          'p',
          'kt-note',
          'Estimated savings scale proportionally with floor area and are not measured results. ' +
          'Reference costs are published 2021 figures for the World Bank model school and are not adjusted for this school.'
        )
      );
    }

    function stat(labelText, valueText, unit) {
      const box = make('div', 'kt-stat');
      box.appendChild(make('div', 'kt-label', labelText));

      const value = make('div', 'kt-value', valueText);
      if (unit) value.appendChild(make('span', 'kt-unit', ` ${unit}`));

      box.appendChild(value);
      return box;
    }

    function renderPackage(target, pkg) {
      if (!target) return;
      target.textContent = '';

      if (!pkg) {
        target.textContent = 'No package results available.';
        return;
      }

      const stats = make('div', 'kt-stats');
      stats.append(
        stat('Baseline heating demand', fmt(pkg.baseline_heating_kwh), 'kWh/yr'),
        stat('After insulation', fmt(pkg.heating_after_insulation_kwh), 'kWh/yr'),
        stat('After package', fmt(pkg.heating_after_package_kwh), 'kWh/yr'),
        stat('Thermal savings', fmt(pkg.thermal_savings_kwh), 'kWh/yr'),
        stat('Electrical savings (LED)', fmt(pkg.electrical_savings_kwh), 'kWh/yr'),
        stat('Total reference cost', usd(pkg.total_investment_cost_usd_2021), '2021 USD')
      );
      target.appendChild(stats);

      target.appendChild(
        make(
          'p',
          'kt-note',
          'Thermal (heat) and electrical savings are different kinds of energy and are reported separately. They are not added together.'
        )
      );

      target.appendChild(make('h4', 'kt-h', 'Measures in this package'));

      const { wrap, body } = buildTable(
        'Measures selected for the package',
        ['Measure', 'Energy type', 'Estimated saving (kWh/yr)', 'Reference cost (2021 USD)']
      );

      (pkg.selected_measures || []).forEach((m) => {
        addRow(body, [
          make('span', 'kt-name', m.intervention),
          m.energy_carrier === 'thermal' ? 'Thermal (heat)' : 'Electrical',
          fmt(m.estimated_saving_kwh),
          usd(m.investment_cost_usd_2021)
        ]);
      });

      target.appendChild(wrap);

      if (pkg.investment_cost_basis) {
        target.appendChild(make('p', 'kt-note', pkg.investment_cost_basis));
      }

      if (Array.isArray(pkg.excluded_options) && pkg.excluded_options.length) {
        target.appendChild(make('h4', 'kt-h', 'Options not included'));

        const ul = make('ul', 'kt-list');

        pkg.excluded_options.forEach((o) => {
          ul.appendChild(make('li', null, `${o.intervention}: ${o.reason}`));
        });

        target.appendChild(ul);
      }

      if (pkg.boiler_assumption) {
        target.appendChild(make('p', 'kt-note', pkg.boiler_assumption));
      }
    }

    function scenarioCard(title, scenario) {
      const card = make('div', 'kt-card');
      card.appendChild(make('h4', null, title));

      const rows = [
        ['Budget', usd(scenario.budget_usd_2021)],
        ['Estimated savings', kwh(scenario.estimated_savings_kwh)],
        ['Reference cost of selection', usd(scenario.investment_cost_usd_2021)],
        ['Budget remaining', usd(scenario.remaining_budget_usd_2021)]
      ];

      rows.forEach(([term, value]) => {
        const row = make('div', 'kt-row');
        row.append(make('span', 'kt-muted', term), make('strong', null, value));
        card.appendChild(row);
      });

      const measures = scenario.selected_measures || [];

      if (measures.length === 0) {
        card.appendChild(
          make('p', 'kt-note', 'No measure fits within this budget.')
        );
      } else {
        const ul = make('ul');

        measures.forEach((m) => {
          const li = make('li');
          li.appendChild(make('strong', null, m.intervention));
          li.appendChild(
            make(
              'div',
              'kt-sub',
              `${kwh(m.estimated_saving_kwh)} saved · ${usd(m.investment_cost_usd_2021)}`
            )
          );
          ul.appendChild(li);
        });

        card.appendChild(ul);
      }

      return card;
    }

    function renderBudget(target, budgetResult) {
      if (!target) return;
      target.textContent = '';

      if (!budgetResult) {
        target.textContent = 'No budget results available.';
        return;
      }

      const cards = make('div', 'kt-cards');

      if (budgetResult.thermal_optimization) {
        cards.appendChild(
          scenarioCard('Heating scenario (thermal)', budgetResult.thermal_optimization)
        );
      }

      if (budgetResult.electrical_optimization) {
        cards.appendChild(
          scenarioCard('Electricity scenario (LED)', budgetResult.electrical_optimization)
        );
      }

      target.appendChild(cards);

      if (budgetResult.cost_basis) {
        target.appendChild(make('p', 'kt-note', budgetResult.cost_basis));
      }

      if (Array.isArray(budgetResult.limitations) && budgetResult.limitations.length) {
        target.appendChild(make('h4', 'kt-h', 'What the optimizer does not do'));

        const ul = make('ul', 'kt-list');

        budgetResult.limitations.forEach((text) => {
          ul.appendChild(make('li', null, text));
        });

        target.appendChild(ul);
      }
    }

    function renderLimitations(target, items) {
      if (!target) return;
      target.textContent = '';

      const list = Array.isArray(items) && items.length
        ? items
        : ['No limitations were returned by the API.'];

      list.forEach((text) => target.appendChild(make('li', null, text)));
    }

    assessmentForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      if (!assessmentForm.reportValidity()) return;

      const form = new FormData(assessmentForm);

      const profile = {
        climate_zone: Number(form.get('climate_zone')),
        floor_area_m2: readNumber(form.get('floor_area_m2')),
        heating_system: form.get('heating_system'),
        heating_condition: form.get('heating_condition'),
        available_fuels: form.getAll('available_fuels'),
        electrical_capacity_kw: readNumber(form.get('electrical_capacity_kw'))
      };

      const budget = readNumber(form.get('budget_usd_2021'));

      if (
        !Number.isFinite(profile.floor_area_m2) ||
        profile.floor_area_m2 <= 0 ||
        !Number.isFinite(budget) ||
        budget < 0
      ) {
        if (assessmentStatus) {
          assessmentStatus.textContent =
            'Please enter a valid floor area and budget.';
        }
        return;
      }

      if (assessmentSubmit) {
        assessmentSubmit.disabled = true;
        assessmentSubmit.textContent = 'Evaluating…';
      }

      if (assessmentStatus) {
        assessmentStatus.textContent = 'Running the model. Please wait.';
      }

      try {
        const response = await fetch('/api/evaluate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            profile,
            budget_usd_2021: budget
          })
        });

        let data;

        try {
          data = await response.json();
        } catch {
          throw new Error('The server returned an invalid response.');
        }

        if (!response.ok || !data.success) {
          throw new Error(
            data.error || `The request failed (${response.status}).`
          );
        }

        renderSummary($('#assessmentSummary'), profile, budget);
        renderMeasures($('#interventionResults'), data.evaluation?.interventions);
        renderPackage($('#packageResults'), data.package);
        renderBudget($('#budgetResults'), data.budget_optimization);
        renderLimitations($('#assessmentLimitations'), data.package?.limitations);

        if (assessmentResults) {
          assessmentResults.hidden = false;
          assessmentResults.scrollIntoView({
            behavior: reduce ? 'auto' : 'smooth',
            block: 'start'
          });
        }

        if (assessmentStatus) {
          assessmentStatus.textContent = 'Assessment complete.';
        }

      } catch (error) {
        if (assessmentStatus) {
          assessmentStatus.textContent =
            `Could not complete the assessment: ${error.message}`;
        }

        console.error('Kilowatt Triage assessment error:', error);

      } finally {
        if (assessmentSubmit) {
          assessmentSubmit.disabled = false;
          assessmentSubmit.innerHTML =
            'Evaluate this school <span aria-hidden="true">↗</span>';
        }
      }
    });
  }

})();