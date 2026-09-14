/* =========================================================
   VYAPAR SETU — Freight Rate Forecasting & ML Module
   ========================================================= */

window.ForecastModule = (function() {
  const data = window.VYAPAR_DATA;
  let activeRouteKey = 'AUHPT_INPPP';
  let retrainCount = 0;

  function renderSVGChart(forecast) {
    const w = 720, h = 280, padL = 45, padR = 25, padT = 20, padB = 40;
    const chartW = w - padL - padR, chartH = h - padT - padB;

    const weeks = forecast.weeks;
    const minVal = Math.floor(Math.min(...weeks.map(w => w.p10)) - 1);
    const maxVal = Math.ceil(Math.max(...weeks.map(w => w.p90)) + 1);

    const getX = (idx) => padL + (idx / (weeks.length - 1)) * chartW;
    const getY = (val) => padT + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;

    // Build P10-P90 Area Path
    let areaD = `M ${getX(0)} ${getY(weeks[0].p90)}`;
    for (let i = 1; i < weeks.length; i++) areaD += ` L ${getX(i)} ${getY(weeks[i].p90)}`;
    for (let i = weeks.length - 1; i >= 0; i--) areaD += ` L ${getX(i)} ${getY(weeks[i].p10)}`;
    areaD += ' Z';

    // Build P50 Median Curve
    let p50D = `M ${getX(0)} ${getY(weeks[0].p50)}`;
    for (let i = 1; i < weeks.length; i++) p50D += ` L ${getX(i)} ${getY(weeks[i].p50)}`;

    // Build Y-Gridlines
    let yTicks = '';
    const step = (maxVal - minVal) / 4;
    for (let i = 0; i <= 4; i++) {
      const v = minVal + i * step;
      const y = getY(v);
      yTicks += `
        <line x1="${padL}" y1="${y}" x2="${w - padR}" y2="${y}" stroke="var(--rule-lite)" stroke-dasharray="2 4"/>
        <text x="${padL - 8}" y="${y + 4}" font-family="IBM Plex Mono" font-size="10" fill="var(--ink-faint)" text-anchor="end">$${v.toFixed(1)}</text>
      `;
    }

    // Build X-Axis Labels & Points
    let xTicks = '', points = '';
    weeks.forEach((wk, i) => {
      const x = getX(i);
      xTicks += `<text x="${x}" y="${h - 12}" font-family="IBM Plex Mono" font-size="9.5" fill="var(--ink-faint)" text-anchor="middle">${wk.week.split(' ')[0]}</text>`;
      
      points += `
        <circle cx="${x}" cy="${getY(wk.p50)}" r="4" fill="var(--brass)"/>
        <title>${wk.week}: P50=$${wk.p50.toFixed(2)} (P10: $${wk.p10.toFixed(2)}, P90: $${wk.p90.toFixed(2)})</title>
      `;
    });

    return `
      <svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="width:100%;height:100%;">
        ${yTicks}
        <!-- P10/P90 Uncertainty Band -->
        <path d="${areaD}" fill="rgba(185,129,46,0.18)" stroke="none"/>
        <!-- P50 Median Forecast Line -->
        <path d="${p50D}" fill="none" stroke="var(--brass)" stroke-width="2.5" stroke-linejoin="round"/>
        ${points}
        ${xTicks}
      </svg>
    `;
  }

  function renderSHAPGroup(drivers) {
    return drivers.map(d => `
      <div class="shap-item">
        <div class="shap-header">
          <span class="shap-name">${d.feature}</span>
          <span class="shap-val ${d.direction}">${d.impact > 0 ? '+' : ''}${d.impact.toFixed(1)}%</span>
        </div>
        <div class="shap-track">
          <div class="shap-fill ${d.direction}" style="width: ${Math.min(Math.abs(d.impact) * 5, 100)}%;"></div>
        </div>
        <div class="field-hint">${d.description}</div>
      </div>
    `).join('');
  }

  function init(container) {
    const forecast = data.FORECASTS[activeRouteKey] || data.FORECASTS['AUHPT_INPPP'];

    container.innerHTML = `
      <div class="module-container">
        <div class="module-header">
          <div class="module-title">
            <h2>Prophet + XGBoost Ensemble Freight Rate Forecast</h2>
            <p>12-Week forward freight rate curve with P10/P50/P90 confidence intervals across 7 East Coast ports.</p>
          </div>
          <div class="head-actions">
            <button class="btn brass" id="btn-retrain-model">⚡ Retrain Model</button>
          </div>
        </div>

        <div class="tile-row">
          <div class="tile accent-brass">
            <div class="t-lbl">Current Spot Rate</div>
            <div class="t-val">$${forecast.currentSpot.toFixed(2)} <span style="font-size:12px;color:var(--ink-dim)">/ tonne</span></div>
            <div class="t-sub">Capesize Australia → Paradip</div>
          </div>
          <div class="tile accent-teal">
            <div class="t-lbl">Forecast P50 Trend</div>
            <div class="t-val" id="p50-trend-val">$14.50 → $17.40</div>
            <div class="t-sub">Peak expected Wk 8 (Nov)</div>
          </div>
          <div class="tile accent-purple">
            <div class="t-lbl">Model Accuracy (MAPE)</div>
            <div class="t-val" id="mape-val">3.42%</div>
            <div class="t-sub">Trained on Baltic Dry Index</div>
          </div>
          <div class="tile accent-blue">
            <div class="t-lbl">Risk Spread (P90 - P10)</div>
            <div class="t-val">$4.00 / t</div>
            <div class="t-sub">IMD Cyclone Season Impact</div>
          </div>
        </div>

        <div class="forecast-layout">
          <!-- Main Forecast Chart Panel -->
          <div class="chart-container-card">
            <div class="chart-header">
              <div>
                <h3 style="margin:0;font-size:15px;color:var(--ink)">Freight Rate Prediction ($/tonne)</h3>
                <span style="font-size:11.5px;color:var(--ink-faint)" id="route-subtitle">${forecast.route} · ${forecast.vesselClass}</span>
              </div>
              <div style="display:flex;gap:12px;align-items:center;">
                <label style="font-size:11px;color:var(--ink-faint);text-transform:uppercase;font-weight:600">Select Route:</label>
                <select id="forecast-route-select" style="max-width:260px;font-size:12px;">
                  <option value="AUHPT_INPPP" selected>Australia (Hay Point) → Paradip (WD-1 Capesize)</option>
                  <option value="AUNTL_INVTZ">Australia (Newcastle) → Vizag (Panamax)</option>
                </select>
              </div>
            </div>

            <div class="chart-svg-frame" id="chart-svg-wrap">
              ${renderSVGChart(forecast)}
            </div>

            <!-- Time Machine Date Slider -->
            <div class="time-machine-bar">
              <label>⏱️ Time-Machine Date Slider:</label>
              <input type="range" id="time-machine-range" min="1" max="12" value="1" step="1">
              <span id="time-machine-label" class="mono" style="font-size:12px;font-weight:600;min-width:140px;text-align:right">Wk 1 (Sep 14, 2026)</span>
            </div>
          </div>

          <!-- SHAP Drivers Sidebar -->
          <div class="panel" style="margin-bottom:0">
            <h3>SHAP Model Explainability</h3>
            <p class="panel-sub" style="margin-bottom:14px">Key features driving the forecast P50 rate shift:</p>
            <div class="shap-bar-group" id="shap-drivers-wrap">
              ${renderSHAPGroup(data.SHAP_DRIVERS)}
            </div>
          </div>
        </div>
      </div>
    `;

    // Event Handlers
    const routeSelect = container.querySelector('#forecast-route-select');
    routeSelect.addEventListener('change', (e) => {
      activeRouteKey = e.target.value;
      const newFc = data.FORECASTS[activeRouteKey];
      container.querySelector('#route-subtitle').textContent = `${newFc.route} · ${newFc.vesselClass}`;
      container.querySelector('#chart-svg-wrap').innerHTML = renderSVGChart(newFc);
    });

    const timeSlider = container.querySelector('#time-machine-range');
    timeSlider.addEventListener('input', (e) => {
      const wkIdx = Number(e.target.value) - 1;
      const fc = data.FORECASTS[activeRouteKey];
      const selectedWk = fc.weeks[wkIdx];
      container.querySelector('#time-machine-label').textContent = `${selectedWk.week}`;
    });

    const retrainBtn = container.querySelector('#btn-retrain-model');
    retrainBtn.addEventListener('click', () => {
      retrainBtn.disabled = true;
      retrainBtn.innerHTML = `⌛ Fitting XGBoost...`;

      setTimeout(() => {
        retrainCount++;
        const newMape = (3.42 - retrainCount * 0.04).toFixed(2) + '%';
        container.querySelector('#mape-val').textContent = newMape;
        
        // Shuffle SHAP slightly for visual demonstration
        const updatedShap = data.SHAP_DRIVERS.map(d => ({
          ...d,
          impact: d.impact + (Math.random() * 2 - 1)
        }));
        container.querySelector('#shap-drivers-wrap').innerHTML = renderSHAPGroup(updatedShap);

        retrainBtn.disabled = false;
        retrainBtn.innerHTML = `⚡ Retrain Model`;
        window.AppController?.showToast(`XGBoost residual model refitted! Updated MAPE: ${newMape}`, 'success');
      }, 900);
    });
  }

  return { init };
})();
