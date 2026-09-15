/* =========================================================
   VYAPAR SETU — Ledger Module
   ========================================================= */

window.LedgerModule = (function() {
  const data = window.VYAPAR_DATA;
  
  const state = {
    category: 'ALL',
    commodities: new Set(),
    maxQty: 600000,
    search: '',
    selectedId: null,
    editingId: null,
    detailSection: 'overview'
  };

  function inrShort(n) {
    const abs = Math.abs(n);
    if (abs >= 1e7) return '₹' + (n / 1e7).toFixed(2) + ' Cr';
    if (abs >= 1e5) return '₹' + (n / 1e5).toFixed(2) + ' L';
    return '₹' + Math.round(n).toLocaleString('en-IN');
  }

  function initials(name) {
    return name.split(' ').filter(w => /^[A-Za-z]/.test(w)).slice(0,2).map(w => w[0]).join('').toUpperCase();
  }

  function daysBetween(a, b) {
    return Math.round((new Date(b) - new Date(a)) / 86400000);
  }

  function todayISO() {
    return '2026-09-14';
  }

  function contractProgress(c) {
    const start = new Date(c.startDate), end = new Date(c.endDate), now = new Date(todayISO());
    if (now <= start) return 0;
    if (now >= end) return 1;
    return (now - start) / (end - start);
  }

  function budgetState(ratio) {
    if (ratio >= 0.92) return 'critical';
    if (ratio >= 0.75) return 'warning';
    return 'healthy';
  }

  function ctaCopy(c) {
    const ratio = c.committedSpend / c.maxBudget, st = budgetState(ratio), prog = contractProgress(c);
    const remaining = c.maxBudget - c.committedSpend;
    const first = c.officer.split(' ')[0];
    if (st === 'critical') {
      return { state: 'critical', head: 'Time to step in',
        body: `${first}, this contract is at ${(ratio*100).toFixed(1)}% of budget with only ${inrShort(remaining)} headroom left. Seek approval before fixing additional freight on ${c.vesselName}.` };
    }
    if (st === 'warning') {
      return { state: 'warning', head: 'Worth a look',
        body: `${(ratio*100).toFixed(1)}% of budget committed (${(prog*100).toFixed(0)}% term elapsed). Check freight forecast before next fixture booking.` };
    }
    return { state: 'healthy', head: 'Nice and steady',
      body: `Spend tracking comfortably at ${(ratio*100).toFixed(1)}% of budget against ${(prog*100).toFixed(0)}% term elapsed. No immediate action required.` };
  }

  function project(lon, lat, w, h) {
    return [((lon + 180) / 360) * w, ((90 - lat) / 180) * h];
  }

  function routeSVG(c) {
    const w = 900, h = 140;
    const origin = data.PORTS[c.originPortCode] || { lon: 149.3, lat: -21.27, name: c.originPortCode };
    const dest = data.PORTS[c.destPortCode] || { lon: 86.61, lat: 20.32, name: c.destPortCode };
    const [x1] = project(origin.lon, origin.lat, w, h);
    const [x2] = project(dest.lon, dest.lat, w, h);
    const pad = 50, px1 = pad, px2 = w - pad, midY = h / 2;
    const prog = contractProgress(c);
    const flip = x1 > x2;
    const startX = flip ? px2 : px1, endX = flip ? px1 : px2;
    const vX = startX + (endX - startX) * prog;
    const curveY = midY - 26;
    return `
    <svg class="route-svg" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
      <path d="M ${px1} ${midY} Q ${w/2} ${curveY} ${px2} ${midY}" fill="none" stroke="var(--rule)" stroke-width="1.5" stroke-dasharray="1 8" stroke-linecap="round"/>
      <path d="M ${startX} ${midY} Q ${w/2} ${curveY} ${vX} ${midY}" fill="none" stroke="none"/>
      <circle cx="${px1}" cy="${midY}" r="5" fill="var(--ink)"/>
      <circle cx="${px2}" cy="${midY}" r="5" fill="var(--ink)"/>
      <text x="${px1}" y="${midY+22}" font-family="IBM Plex Mono" font-size="11" fill="var(--ink-dim)" text-anchor="start">${c.originPortCode}</text>
      <text x="${px2}" y="${midY+22}" font-family="IBM Plex Mono" font-size="11" fill="var(--ink-dim)" text-anchor="end">${c.destPortCode}</text>
      <g transform="translate(${vX},${midY - Math.sin(prog * Math.PI) * 20})">
        <circle r="10" fill="var(--card)" stroke="var(--teal)" stroke-width="2"/>
        <path d="M -3,-2.5 L 4,0 L -3,2.5 Z" fill="var(--teal)"/>
      </g>
    </svg>`;
  }

  function filteredContracts() {
    return data.CONTRACTS.filter(c => {
      if (state.category !== 'ALL' && c.category !== state.category) return false;
      if (state.commodities.size > 0 && !state.commodities.has(c.commodityName)) return false;
      if (c.quantity > state.maxQty) return false;
      if (state.search) {
        const q = state.search.toLowerCase();
        const origin = data.PORTS[c.originPortCode]?.name || '';
        const dest = data.PORTS[c.destPortCode]?.name || '';
        const hay = `${c.title} ${c.id} ${c.vesselName} ${origin} ${dest} ${c.commodityName}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  function renderFilters(container) {
    container.innerHTML = `
      <div class="filt-block">
        <p class="filt-title">Search Ledger</p>
        <input type="text" id="f-search" placeholder="Contract ID, vessel, port…" value="${state.search}">
      </div>
      <details class="filt-collapse" open>
        <summary>Commodity Filter</summary>
        <div class="inner">
          <div id="commodity-list"></div>
          <div class="add-commodity-row">
            <input type="text" id="f-add-commodity" placeholder="Add commodity…">
            <button class="btn ghost small" id="f-add-commodity-btn">Add</button>
          </div>
        </div>
      </details>
      <details class="filt-collapse">
        <summary>Quantity Cap</summary>
        <div class="inner">
          <input type="range" id="f-qty" min="0" max="600000" step="10000" value="${state.maxQty}">
          <div class="range-labels"><span>0</span><span id="f-qty-val">${state.maxQty.toLocaleString('en-IN')} MT</span></div>
        </div>
      </details>
      <button class="clear-btn" id="f-clear">Reset Filters</button>
    `;

    renderCommodityList(container.querySelector('#commodity-list'));

    container.querySelector('#f-search').addEventListener('input', e => {
      state.search = e.target.value;
      renderList(document.getElementById('listpane'));
    });
    container.querySelector('#f-qty').addEventListener('input', e => {
      state.maxQty = Number(e.target.value);
      container.querySelector('#f-qty-val').textContent = state.maxQty.toLocaleString('en-IN') + ' MT';
      renderList(document.getElementById('listpane'));
    });
    container.querySelector('#f-clear').addEventListener('click', () => {
      state.commodities.clear(); state.maxQty = 600000; state.search = ''; state.category = 'ALL';
      renderFilters(container);
      renderList(document.getElementById('listpane'));
    });
    container.querySelector('#f-add-commodity-btn').addEventListener('click', () => {
      const input = container.querySelector('#f-add-commodity');
      const val = input.value.trim();
      if (!val) return;
      if (!data.COMMODITIES.includes(val)) data.COMMODITIES.push(val);
      input.value = '';
      renderCommodityList(container.querySelector('#commodity-list'));
    });
  }

  function renderCommodityList(wrap) {
    if (!wrap) return;
    wrap.innerHTML = data.COMMODITIES.slice().sort().map(name => {
      const count = data.CONTRACTS.filter(c => c.commodityName === name).length;
      const checked = state.commodities.has(name) ? 'checked' : '';
      return `<div class="commodity-row">
        <label><input type="checkbox" data-commodity="${name}" ${checked}> ${name} <span class="n">(${count})</span></label>
      </div>`;
    }).join('');

    wrap.querySelectorAll('[data-commodity]').forEach(cb => {
      cb.addEventListener('change', e => {
        const v = e.target.dataset.commodity;
        if (e.target.checked) state.commodities.add(v); else state.commodities.delete(v);
        renderList(document.getElementById('listpane'));
      });
    });
  }

  function renderList(container) {
    if (!container) return;
    const list = filteredContracts();
    if (state.selectedId !== null && !list.find(c => c.id === state.selectedId) && list.length > 0) {
      state.selectedId = list[0].id;
    }
    if (list.length === 0) state.selectedId = null;

    container.innerHTML = `
      <div class="list-toolbar">
        <div class="list-toolbar-row">
          <h2>All Contracts</h2>
          <select class="cat-select" id="cat-select">
            <option value="ALL">All Categories</option>
            <option value="SINGLE_SPOT">Single Spot</option>
            <option value="SHORT_TERM">Short Term</option>
            <option value="LONG_TERM">Long Term</option>
          </select>
        </div>
        <div class="list-toolbar-row">
          <span class="list-count">${list.length} matching contract${list.length === 1 ? '' : 's'}</span>
        </div>
      </div>
      <div id="card-list">
      ${list.length === 0
        ? `<div class="empty">No contracts match current filters.</div>`
        : list.map(c => {
            const ratio = c.committedSpend / c.maxBudget;
            const st = budgetState(ratio);
            const fillColor = st === 'critical' ? 'var(--red)' : st === 'warning' ? 'var(--brass)' : 'var(--teal)';
            const catLabel = { SINGLE_SPOT: 'Single Spot', SHORT_TERM: 'Short Term', LONG_TERM: 'Long Term' }[c.category];
            return `
            <div class="card ${c.id === state.selectedId ? 'active' : ''}" data-id="${c.id}">
              <div class="card-top">
                <span class="card-id">${c.id}</span>
                <span class="tag ${c.category}">${catLabel}</span>
              </div>
              <div class="card-title">${c.title}</div>
              <div class="card-meta">
                <span>${c.commodityName}</span>
                <span class="route">${c.originPortCode} → ${c.destPortCode}</span>
              </div>
              <div class="card-officer">
                <span class="avatar">${initials(c.officer)}</span>
                <span>${c.officer.split(' · ')[0]}</span>
              </div>
              <div class="card-bud">
                <div class="bud-bar"><div class="bud-fill" style="width:${Math.min(ratio*100, 100)}%;background:${fillColor}"></div></div>
                <div class="bud-row"><span>${inrShort(c.committedSpend)} committed</span><span>${(ratio*100).toFixed(0)}% of ${inrShort(c.maxBudget)}</span></div>
              </div>
            </div>`;
          }).join('')
      }
      </div>`;

    container.querySelector('#cat-select').value = state.category;
    container.querySelector('#cat-select').addEventListener('change', e => {
      state.category = e.target.value;
      renderList(container);
    });

    container.querySelectorAll('.card').forEach(card => {
      card.addEventListener('click', () => {
        state.selectedId = card.dataset.id;
        state.detailSection = 'overview';
        renderList(container);
        renderDetail(document.getElementById('detail'));
      });
    });
  }

  function globalWorldMapSVG() {
    const w = 900, h = 420;
    
    // Grid lines (latitudes / longitudes)
    const latLines = [60, 30, 0, -30, -60].map(lat => {
      const y = Math.round(((90 - lat) / 180) * h);
      return `<line x1="0" y1="${y}" x2="${w}" y2="${y}" stroke="rgba(185,129,46,0.12)" stroke-dasharray="3 4" stroke-width="1"/>
              <text x="12" y="${y - 4}" font-family="IBM Plex Mono" font-size="9" fill="rgba(42,32,22,0.4)">${lat > 0 ? lat + '°N' : lat < 0 ? Math.abs(lat) + '°S' : 'Equator (0°)'}</text>`;
    }).join('');

    const lonLines = [-120, -60, 0, 60, 120].map(lon => {
      const x = Math.round(((lon + 180) / 360) * w);
      return `<line x1="${x}" y1="0" x2="${x}" y2="${h}" stroke="rgba(185,129,46,0.12)" stroke-dasharray="3 4" stroke-width="1"/>
              <text x="${x + 4}" y="${h - 10}" font-family="IBM Plex Mono" font-size="9" fill="rgba(42,32,22,0.4)">${lon > 0 ? lon + '°E' : lon < 0 ? Math.abs(lon) + '°W' : '0°'}</text>`;
    }).join('');

    // Coastlines & Landmass Polygons (equirectangular projection)
    const africaPath = "M 407 137 L 477 132 L 530 147 L 535 157 L 557 195 L 577 197 L 572 222 L 550 250 L 537 287 L 515 307 L 495 310 L 480 267 L 472 215 L 412 195 Z";
    const eurasiaPath = "M 425 135 L 450 117 L 487 80 L 525 50 L 625 45 L 800 50 L 875 75 L 800 137 L 750 150 L 712 200 L 700 217 L 695 205 L 675 170 L 650 192 L 632 187 L 620 165 L 595 162 L 557 195 L 532 157 L 512 125 L 475 115 Z";
    const indiaPath = "M 620 165 L 635 185 L 642 200 L 650 205 L 660 195 L 668 180 L 675 170 L 678 165 L 660 150 L 630 152 Z";
    const australiaPath = "M 732 280 L 760 262 L 790 255 L 805 252 L 825 282 L 832 295 L 825 317 L 795 312 L 737 310 Z";
    const northAmericaPath = "M 30 62 L 100 75 L 137 105 L 150 140 L 187 175 L 225 187 L 250 205 L 262 137 L 287 115 L 300 100 L 250 62 L 150 50 Z";
    const southAmericaPath = "M 250 205 L 262 250 L 275 270 L 270 337 L 287 362 L 325 300 L 362 237 L 325 200 L 262 200 Z";

    // Global Trade Routes (Arcs connecting suppliers to India)
    const routes = [
      { id: 'au-in', path: 'M 829 307 Q 750 220 666 174', color: 'var(--brass)' },
      { id: 'mz-in', path: 'M 531 290 Q 600 250 666 174', color: 'var(--teal)' },
      { id: 'us-in', path: 'M 258 127 Q 380 320 666 174', color: '#7c3aed' },
      { id: 'id-in', path: 'M 744 226 Q 700 200 666 174', color: '#2563eb' },
      { id: 'ru-in', path: 'M 783 118 Q 740 140 666 174', color: '#d97706' }
    ];

    const routeSVGs = routes.map(r => `
      <path d="${r.path}" fill="none" stroke="${r.color}" stroke-width="2.2" stroke-dasharray="6 6" opacity="0.85">
        <animate attributeName="stroke-dashoffset" from="24" to="0" dur="2s" repeatCount="indefinite" />
      </path>
    `).join('');

    // Ports Pins
    const ports = [
      { name: 'Paradip (INPPP)', x: 666, y: 174, hub: true },
      { name: 'Dhamra (INDHM)', x: 667, y: 168, hub: true },
      { name: 'Vizag (INVTZ)', x: 658, y: 181, hub: true },
      { name: 'Newcastle (AUNTL)', x: 829, y: 307, hub: false },
      { name: 'Hay Point (AUHPT)', x: 823, y: 278, hub: false },
      { name: 'Maputo (MZMAP)', x: 531, y: 290, hub: false },
      { name: 'Baltimore (USBAL)', x: 258, y: 127, hub: false },
      { name: 'Tanjung Bara (IDTAB)', x: 744, y: 226, hub: false },
      { name: 'Vostochny (RUVOST)', x: 783, y: 118, hub: false }
    ];

    const portMarkers = ports.map(p => {
      if (p.hub) {
        return `
          <g transform="translate(${p.x},${p.y})">
            <circle r="10" fill="rgba(30,110,99,0.25)">
              <animate attributeName="r" values="6;14;6" dur="3s" repeatCount="indefinite"/>
              <animate attributeName="opacity" values="0.7;0.1;0.7" dur="3s" repeatCount="indefinite"/>
            </circle>
            <circle r="4.5" fill="var(--teal)" stroke="var(--paper)" stroke-width="1.5"/>
            <text x="9" y="3.5" font-family="IBM Plex Mono" font-size="10" font-weight="600" fill="var(--teal)">${p.name}</text>
          </g>`;
      } else {
        return `
          <g transform="translate(${p.x},${p.y})">
            <circle r="4" fill="var(--brass)" stroke="var(--paper)" stroke-width="1.2"/>
            <text x="7" y="-3" font-family="IBM Plex Mono" font-size="9.5" font-weight="500" fill="var(--ink-dim)">${p.name}</text>
          </g>`;
      }
    }).join('');

    return `
      <svg class="global-map-svg" viewBox="0 0 ${w} ${h}" style="width:100%;height:350px;display:block;background:var(--paper);border-radius:4px;border:1px solid var(--rule);">
        <!-- Map Background & Grid -->
        <rect width="${w}" height="${h}" fill="rgba(30,110,99,0.03)" />
        ${latLines}
        ${lonLines}

        <!-- Landmass Polygons -->
        <path d="${africaPath}" fill="rgba(214, 199, 167, 0.45)" stroke="rgba(185, 129, 46, 0.4)" stroke-width="1" />
        <path d="${eurasiaPath}" fill="rgba(214, 199, 167, 0.45)" stroke="rgba(185, 129, 46, 0.4)" stroke-width="1" />
        <path d="${indiaPath}" fill="rgba(30, 110, 99, 0.2)" stroke="var(--teal)" stroke-width="1.5" />
        <path d="${australiaPath}" fill="rgba(214, 199, 167, 0.45)" stroke="rgba(185, 129, 46, 0.4)" stroke-width="1" />
        <path d="${northAmericaPath}" fill="rgba(214, 199, 167, 0.45)" stroke="rgba(185, 129, 46, 0.4)" stroke-width="1" />
        <path d="${southAmericaPath}" fill="rgba(214, 199, 167, 0.45)" stroke="rgba(185, 129, 46, 0.4)" stroke-width="1" />

        <!-- Compass Decoration -->
        <g transform="translate(60, 360)">
          <circle r="20" fill="none" stroke="rgba(185,129,46,0.3)" stroke-width="1"/>
          <line x1="0" y1="-24" x2="0" y2="24" stroke="rgba(185,129,46,0.5)" stroke-width="1.2"/>
          <line x1="-24" y1="0" x2="24" y2="0" stroke="rgba(185,129,46,0.5)" stroke-width="1.2"/>
          <text x="-3.5" y="-26" font-family="Fraunces" font-size="10" font-weight="700" fill="var(--brass)">N</text>
        </g>

        <!-- Global Maritime Shipping Routes -->
        ${routeSVGs}

        <!-- Port Pins -->
        ${portMarkers}
      </svg>
    `;
  }

  function renderGlobalMap() {
    return `
      <div class="detail-nav">
        <div class="dn-head">
          <div class="dn-id" style="background:var(--teal);color:#fff;padding:2px 8px;border-radius:3px;font-size:11px;">GLOBAL</div>
        </div>
        <button class="active" style="cursor:default;">🌐 Global Trade Network Map</button>
      </div>

      <div class="detail-content" style="padding:20px;">
        <div class="d-head" style="margin-bottom:16px;">
          <div>
            <div class="d-title" style="font-size:18px;font-weight:700;">Global Maritime Trade Corridors</div>
            <div style="font-size:12px;color:var(--ink-faint);margin-top:2px;">Monitoring 7 East Coast India Ports &amp; Global Raw Material Supply Basins</div>
          </div>
          <div class="d-badges">
            <span class="tag LONG_TERM">7 East Coast Ports</span>
            <span class="tag SINGLE_SPOT">Global AIS Tracked</span>
          </div>
        </div>

        <div class="tile-row" style="margin-bottom:16px;">
          <div class="tile accent-teal"><div class="t-lbl">East Coast Hubs</div><div class="t-val">7 Ports</div><div class="t-sub">Paradip · Dhamra · Vizag</div></div>
          <div class="tile accent-brass"><div class="t-lbl">Supply Basins</div><div class="t-val">5 Origins</div><div class="t-sub">Australia · Mozambique · USA</div></div>
          <div class="tile accent-purple"><div class="t-lbl">Monitored Cargo</div><div class="t-val">4.8M MT</div><div class="t-sub">Coking Coal · LNG · Pellets</div></div>
        </div>

        <div class="panel" style="padding:14px;margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <h3 style="margin:0;">World Freight Flow &amp; Maritime Lanes</h3>
            <span style="font-size:11px;font-family:'IBM Plex Mono',monospace;color:var(--teal);">● REAL-TIME GLOBAL AIS OVERLAY</span>
          </div>
          ${globalWorldMapSVG()}
          
          <div style="display:flex;gap:18px;margin-top:12px;font-size:11.5px;color:var(--ink-dim);flex-wrap:wrap;align-items:center;">
            <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--teal);margin-right:4px;"></span><b>East Coast Discharge Ports</b></span>
            <span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--brass);margin-right:4px;"></span><b>Global Origin Basins</b></span>
            <span><span style="display:inline-block;width:16px;height:2px;background:var(--brass);margin-right:4px;vertical-align:middle;"></span><b>Coking Coal Corridors</b></span>
          </div>
        </div>

        <div class="panel">
          <h3>Active Vessels &amp; Contracts</h3>
          <p style="font-size:12px;color:var(--ink-dim);margin-bottom:12px;">Select any vessel below or from the ledger list on the left to inspect detailed AIS position, IMO specs, and voyage ETA:</p>
          <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(240px, 1fr));gap:10px;">
            ${data.CONTRACTS.map(c => `
              <div class="card contract-quick-select" data-id="${c.id}" style="margin:0;cursor:pointer;padding:12px;">
                <div class="card-top">
                  <span class="card-id">${c.id}</span>
                  <span class="tag ${c.category}">${c.category}</span>
                </div>
                <div class="card-title" style="font-size:13px;margin:6px 0 4px 0;">${c.vesselName}</div>
                <div class="card-meta" style="font-size:11px;">
                  <span>${c.commodityName}</span>
                  <span class="route">${c.originPortCode} → ${c.destPortCode}</span>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  function bindGlobalMapEvents(container) {
    if (!container) return;
    container.querySelectorAll('.contract-quick-select').forEach(card => {
      card.addEventListener('click', () => {
        state.selectedId = card.dataset.id;
        state.detailSection = 'overview';
        renderList(document.getElementById('listpane'));
        renderDetail(container);
      });
    });
  }

  function renderDetail(container) {
    if (!container) return;
    const c = data.CONTRACTS.find(x => x.id === state.selectedId);
    if (!c) {
      container.innerHTML = renderGlobalMap();
      bindGlobalMapEvents(container);
      return;
    }

    const sections = [
      { id: 'overview', label: 'Overview' },
      { id: 'budget', label: 'Budget' },
      { id: 'vessel', label: 'Vessel & Map' },
      { id: 'details', label: 'Full Details' }
    ];

    container.innerHTML = `
      <div class="detail-nav">
        <div class="dn-head">
          <div class="dn-id">${c.id}</div>
        </div>
        ${sections.map(s => `<button data-sec="${s.id}" class="${state.detailSection === s.id ? 'active' : ''}">${s.label}</button>`).join('')}
        <button id="btn-show-global-map" class="btn ghost small" style="margin-left:auto;font-size:11px;color:var(--teal);border:1px solid var(--rule-lite);">🌐 Global Map</button>
      </div>
      <div class="detail-content" id="detail-content"></div>
    `;

    container.querySelectorAll('.detail-nav button[data-sec]').forEach(b => {
      b.addEventListener('click', () => {
        state.detailSection = b.dataset.sec;
        renderDetail(container);
      });
    });

    container.querySelector('#btn-show-global-map')?.addEventListener('click', () => {
      state.selectedId = null;
      renderList(document.getElementById('listpane'));
      renderDetail(container);
    });

    renderDetailContent(c, container.querySelector('#detail-content'));
  }

  function renderDetailContent(c, content) {
    if (!content) return;
    const cta = ctaCopy(c);
    const prog = contractProgress(c);
    const ratio = c.committedSpend / c.maxBudget;
    const gaugeColor = cta.state === 'critical' ? 'var(--red)' : cta.state === 'warning' ? 'var(--brass)' : 'var(--teal)';
    const remaining = c.maxBudget - c.committedSpend;
    const origin = data.PORTS[c.originPortCode] || { name: c.originPortCode };
    const dest = data.PORTS[c.destPortCode] || { name: c.destPortCode };
    const durationDays = daysBetween(c.startDate, c.endDate);
    const catLabel = { SINGLE_SPOT: 'Single Spot', SHORT_TERM: 'Short Term', LONG_TERM: 'Long Term' }[c.category];

    const head = `
      <div class="d-head">
        <div class="d-id">IMO ${c.vesselImo}</div>
        <div class="d-title">${c.title}</div>
        <div class="d-badges">
          <span class="tag ${c.category}">${catLabel}</span>
          <span class="d-officer"><span class="avatar">${initials(c.officer)}</span>${c.officer}</span>
        </div>
        <div class="d-actions">
          <button class="btn ghost small" id="btn-edit-contract">Edit Contract</button>
          <button class="btn danger small" id="btn-delete-contract">Delete</button>
        </div>
      </div>`;

    let body = '';
    if (state.detailSection === 'overview') {
      body = `
        <div class="tile-row">
          <div class="tile accent-brass"><div class="t-lbl">Budget Committed</div><div class="t-val">${(ratio*100).toFixed(0)}%</div><div class="t-sub">${inrShort(c.committedSpend)} of ${inrShort(c.maxBudget)}</div></div>
          <div class="tile accent-teal"><div class="t-lbl">Transit Elapsed</div><div class="t-val">${(prog*100).toFixed(0)}%</div><div class="t-sub">${c.startDate} → ${c.endDate}</div></div>
          <div class="tile accent-purple"><div class="t-lbl">Cargo Parcel</div><div class="t-val">${(c.quantity/1000).toFixed(0)}k MT</div><div class="t-sub">${c.commodityName}</div></div>
        </div>
        <div class="panel">
          <h3>Route at a Glance</h3>
          <div class="route-ports">
            <div class="route-port"><div class="code">${c.originPortCode}</div><div class="name">${origin.name}</div></div>
            <div class="route-port dest"><div class="code">${c.destPortCode}</div><div class="name">${dest.name}</div></div>
          </div>
        </div>
        ${c.note ? `<div class="panel"><h3>Desk Note</h3><div class="note-box" style="padding-top:0;border-top:none;margin-top:0;">"${c.note}"</div></div>` : ''}
      `;
    } else if (state.detailSection === 'budget') {
      body = `
        <div class="panel">
          <h3>Max Procurement Budget Ceiling</h3>
          <div class="gauge-wrap">
            <svg width="92" height="92" viewBox="0 0 88 88">
              <circle cx="44" cy="44" r="38" fill="none" stroke="var(--rule-lite)" stroke-width="8"/>
              <circle cx="44" cy="44" r="38" fill="none" stroke="${gaugeColor}" stroke-width="8"
                stroke-dasharray="${2*Math.PI*38}" stroke-dashoffset="${2*Math.PI*38*(1-Math.min(ratio,1))}"
                stroke-linecap="round" transform="rotate(-90 44 44)"/>
              <text x="44" y="49" text-anchor="middle" font-family="IBM Plex Mono" font-size="15" fill="var(--ink)" font-weight="600">${(ratio*100).toFixed(0)}%</text>
            </svg>
            <div class="gauge-figs">
              <div class="big">${inrShort(c.committedSpend)}</div>
              <div class="lbl">committed of ${inrShort(c.maxBudget)} max ceiling</div>
              <div class="of">${inrShort(remaining)} remaining headroom</div>
            </div>
          </div>
        </div>
        <div class="panel">
          <h3>Desk Recommendation</h3>
          <div class="cta ${cta.state}">
            <span class="dot"></span>
            <div><div class="head">${cta.head}</div><div class="body">${cta.body}</div></div>
          </div>
        </div>
      `;
    } else if (state.detailSection === 'vessel') {
      body = `
        <div class="panel">
          <h3>${c.vesselName} · IMO ${c.vesselImo}</h3>
          <div class="route-ports">
            <div class="route-port"><div class="code">${c.originPortCode}</div><div class="name">${origin.name}</div></div>
            <div class="route-port dest"><div class="code">${c.destPortCode}</div><div class="name">${dest.name}</div></div>
          </div>
          <div class="chart-frame">${routeSVG(c)}</div>
          <div class="route-info">
            <span><b>${(prog*100).toFixed(0)}%</b> transit window elapsed</span>
            <span>${durationDays} days total voyage duration</span>
          </div>
          <div class="mt-row">
            <span class="mt-caption">Track live AIS positions via MarineTraffic</span>
            <a class="btn teal small" href="https://www.marinetraffic.com/en/ais/details/ships/imo:${c.vesselImo}" target="_blank" rel="noopener">Track on MarineTraffic ↗</a>
          </div>
        </div>
      `;
    } else {
      body = `
        <div class="panel">
          <h3>Contract Details & Specifications</h3>
          <table class="meta-table">
            <tr><td>Commodity</td><td>${c.commodityName} (${c.commodityCode})</td></tr>
            <tr><td>Quantity</td><td>${c.quantity.toLocaleString('en-IN')} ${c.unit}</td></tr>
            <tr><td>Origin Port</td><td>${origin.name} (${c.originPortCode})</td></tr>
            <tr><td>Destination Port</td><td>${dest.name} (${c.destPortCode})</td></tr>
            <tr><td>Contract Term</td><td>${c.startDate} — ${c.endDate}</td></tr>
            <tr><td>Duration</td><td>${durationDays} days</td></tr>
            <tr><td>Vessel Name</td><td>${c.vesselName}</td></tr>
            <tr><td>IMO Number</td><td>${c.vesselImo}</td></tr>
            <tr><td>Desk Officer</td><td>${c.officer}</td></tr>
          </table>
          ${c.note ? `<div class="note-box">"${c.note}"</div>` : ''}
        </div>
      `;
    }

    content.innerHTML = head + body;

    content.querySelector('#btn-edit-contract')?.addEventListener('click', () => openModal(c.id));
    content.querySelector('#btn-delete-contract')?.addEventListener('click', () => deleteContract(c.id));
  }

  function openModal(id) {
    state.editingId = id;
    const editing = id ? data.CONTRACTS.find(c => c.id === id) : null;
    const portOptions = Object.entries(data.PORTS).map(([code, p]) => `<option value="${code}">${p.name} (${code})</option>`).join('');
    const commodityOptions = data.COMMODITIES.slice().sort().map(name => `<option value="${name}">${name}</option>`).join('');
    const officerOptions = data.OFFICERS.map(o => `<option value="${o}">${o}</option>`).join('');

    const v = editing || {
      title: '', category: 'SINGLE_SPOT', commodityName: data.COMMODITIES[0] || '', commodityCode: 'COMM-GEN-100',
      quantity: 55000, unit: 'Metric Tons', startDate: '2026-09-15', endDate: '2026-10-15',
      originPortCode: 'AUNTL', destPortCode: 'INPPP', vesselImo: 9812400, vesselName: 'MV Paradip Express',
      maxBudget: 1200000000, committedSpend: 850000000, officer: data.OFFICERS[0], note: ''
    };

    const root = document.getElementById('modal-root');
    root.innerHTML = `
      <div class="modal-overlay" id="modal-overlay">
        <div class="modal">
          <h2>${editing ? 'Edit Contract' : 'New Trade Contract'}</h2>
          <div class="modal-sub">${editing ? editing.id : 'Filing as CNT-2026-00' + (data.CONTRACTS.length + 1)}</div>
          <div class="form-grid">
            <div class="field full"><label>Contract Title</label>
              <input type="text" id="m-title" value="${v.title.replace(/"/g, '&quot;')}" placeholder="e.g. Newcastle Coking Coal — SAIL Paradip WD-1"></div>
            <div class="field"><label>Category</label>
              <select id="m-category">
                <option value="SINGLE_SPOT" ${v.category==='SINGLE_SPOT'?'selected':''}>Single Spot</option>
                <option value="SHORT_TERM" ${v.category==='SHORT_TERM'?'selected':''}>Short Term</option>
                <option value="LONG_TERM" ${v.category==='LONG_TERM'?'selected':''}>Long Term</option>
              </select></div>
            <div class="field"><label>Commodity</label><select id="m-commodity">${commodityOptions}</select></div>
            <div class="field"><label>Commodity Code</label><input type="text" id="m-commoditycode" value="${v.commodityCode}"></div>
            <div class="field"><label>Quantity (MT)</label><input type="number" id="m-quantity" value="${v.quantity}"></div>
            <div class="field"><label>Start Date</label><input type="date" id="m-start" value="${v.startDate}"></div>
            <div class="field"><label>End Date</label><input type="date" id="m-end" value="${v.endDate}"></div>
            <div class="field"><label>Origin Port</label><select id="m-origin">${portOptions}</select></div>
            <div class="field"><label>Destination Port</label><select id="m-dest">${portOptions}</select></div>
            <div class="field"><label>Vessel Name</label><input type="text" id="m-vesselname" value="${v.vesselName}"></div>
            <div class="field"><label>IMO Number</label><input type="number" id="m-vesselimo" value="${v.vesselImo}"></div>
            <div class="field"><label>Max Budget (₹)</label><input type="number" id="m-maxbudget" value="${v.maxBudget}"></div>
            <div class="field"><label>Committed Spend (₹)</label><input type="number" id="m-committed" value="${v.committedSpend}"></div>
            <div class="field full"><label>Desk Officer</label><select id="m-officer">${officerOptions}</select></div>
            <div class="field full"><label>Desk Note</label><input type="text" id="m-note" value="${(v.note||'').replace(/"/g,'&quot;')}"></div>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" id="m-cancel">Cancel</button>
            <div class="right"><button class="btn brass" id="m-save">${editing ? 'Save Changes' : 'Add Contract'}</button></div>
          </div>
        </div>
      </div>`;

    root.querySelector('#m-commodity').value = v.commodityName;
    root.querySelector('#m-origin').value = v.originPortCode;
    root.querySelector('#m-dest').value = v.destPortCode;
    root.querySelector('#m-officer').value = v.officer;

    root.querySelector('#m-cancel').addEventListener('click', () => root.innerHTML = '');
    root.querySelector('#modal-overlay').addEventListener('click', e => { if (e.target.id === 'modal-overlay') root.innerHTML = ''; });
    root.querySelector('#m-save').addEventListener('click', saveContract);
  }

  function saveContract() {
    const root = document.getElementById('modal-root');
    const title = root.querySelector('#m-title').value.trim();
    if (!title) { alert('Contract title is required.'); return; }
    
    const payload = {
      title,
      category: root.querySelector('#m-category').value,
      commodityName: root.querySelector('#m-commodity').value,
      commodityCode: root.querySelector('#m-commoditycode').value.trim() || 'COMM-GEN-100',
      quantity: Number(root.querySelector('#m-quantity').value) || 0,
      unit: 'Metric Tons',
      startDate: root.querySelector('#m-start').value,
      endDate: root.querySelector('#m-end').value,
      originPortCode: root.querySelector('#m-origin').value,
      destPortCode: root.querySelector('#m-dest').value,
      vesselName: root.querySelector('#m-vesselname').value.trim() || 'Unnamed Vessel',
      vesselImo: Number(root.querySelector('#m-vesselimo').value) || 0,
      maxBudget: Number(root.querySelector('#m-maxbudget').value) || 0,
      committedSpend: Number(root.querySelector('#m-committed').value) || 0,
      officer: root.querySelector('#m-officer').value,
      note: root.querySelector('#m-note').value.trim()
    };

    if (state.editingId) {
      const idx = data.CONTRACTS.findIndex(c => c.id === state.editingId);
      data.CONTRACTS[idx] = { ...data.CONTRACTS[idx], ...payload };
      state.selectedId = state.editingId;
    } else {
      const newId = `CNT-2026-00${data.CONTRACTS.length + 1}`;
      data.CONTRACTS.push({ id: newId, ...payload });
      state.selectedId = newId;
    }

    root.innerHTML = '';
    renderList(document.getElementById('listpane'));
    renderDetail(document.getElementById('detail'));
    window.AppController?.showToast('Contract ledger updated successfully!', 'success');
  }

  function deleteContract(id) {
    if (!confirm('Remove this contract from the ledger?')) return;
    data.CONTRACTS = data.CONTRACTS.filter(c => c.id !== id);
    if (state.selectedId === id) state.selectedId = data.CONTRACTS[0] ? data.CONTRACTS[0].id : null;
    renderList(document.getElementById('listpane'));
    renderDetail(document.getElementById('detail'));
    window.AppController?.showToast('Contract deleted.', 'info');
  }

  function init(wrapper) {
    wrapper.innerHTML = `
      <div id="body-grid">
        <aside class="filters" id="filters"></aside>
        <section class="listpane" id="listpane"></section>
        <section class="detail" id="detail"></section>
      </div>
    `;
    renderFilters(wrapper.querySelector('#filters'));
    renderList(wrapper.querySelector('#listpane'));
    renderDetail(wrapper.querySelector('#detail'));
  }

  return { init, openModal };
})();
