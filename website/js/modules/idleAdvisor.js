/* =========================================================
   VYAPAR SETU — Idle & Deadheading Advisor Module
   ========================================================= */

window.IdleAdvisorModule = (function() {
  const data = window.VYAPAR_DATA;

  function init(container) {
    container.innerHTML = `
      <div class="module-container">
        <div class="module-header">
          <div class="module-title">
            <h2>Idle & Deadheading Advisor (Post-Discharge Next Voyage Engine)</h2>
            <p>Minimizes vessel idle time at East Coast anchorages by analyzing 2–4 week forecast demand across all 7 ports to recommend ballast, backhaul, or relet strategies.</p>
          </div>
          <div class="head-actions">
            <button class="btn purple" id="btn-run-idle-advisor">⚓ Analyze Vessel Positions</button>
          </div>
        </div>

        <div class="tile-row">
          <div class="tile accent-purple">
            <div class="t-lbl">Current Vessel Position</div>
            <div class="t-val">MV Odisha Titan</div>
            <div class="t-sub">Discharged @ Paradip WD-1</div>
          </div>
          <div class="tile accent-teal">
            <div class="t-lbl">Recommended Strategy</div>
            <div class="t-val" style="color:var(--teal)">Backhaul Triangulation</div>
            <div class="t-sub">Paradip → China (Iron Ore Pellets)</div>
          </div>
          <div class="tile accent-brass">
            <div class="t-lbl">Idle Days Avoided</div>
            <div class="t-val">6.5 Days</div>
            <div class="t-sub">Saves $97,500 Demurrage</div>
          </div>
          <div class="tile accent-blue">
            <div class="t-lbl">Net Voyage Margin</div>
            <div class="t-val">+$182,000</div>
            <div class="t-sub">Covers 82% Ballast Bunker</div>
          </div>
        </div>

        <!-- 3 Strategy Recommendations Grid -->
        <div class="panel">
          <h3>Post-Discharge 3-Way Positioning Recommendations</h3>
          <div class="decision-tree-grid">
            
            <!-- Strategy 1: Backhaul Triangulation (RECOMMENDED) -->
            <div class="decision-card recommended">
              <span class="badge-recommended">★ Optimal Strategy</span>
              <h4>1. Backhaul Triangulation</h4>
              <p style="font-size:12px;color:var(--ink-dim)">Load 150,000 MT Iron Ore Pellets at Paradip for Qingdao (China) return voyage.</p>
              <div class="decision-cost" style="color:var(--teal)">+$182,000 <span style="font-size:12px;font-weight:normal">net earnings</span></div>
              <table class="meta-table" style="font-size:11.5px">
                <tr><td>Freight Revenue</td><td>+$1,350,000 ($9.00/t)</td></tr>
                <tr><td>Bunker Fuel Cost</td><td>-$820,000 (VLSFO)</td></tr>
                <tr><td>Port & Laytime</td><td>-$348,000</td></tr>
                <tr><td>Idle Anchorage Time</td><td><span class="tag HEALTHY">0.5 Days</span></td></tr>
              </table>
              <button class="btn brass small full" style="margin-top:14px;width:100%;justify-content:center" id="btn-select-backhaul">Fix Backhaul Fixture</button>
            </div>

            <!-- Strategy 2: Ballast Reposition -->
            <div class="decision-card">
              <h4>2. Ballast Reposition</h4>
              <p style="font-size:12px;color:var(--ink-dim)">Ballast empty to Hay Point (Australia) for next scheduled SAIL coking coal lifting.</p>
              <div class="decision-cost" style="color:var(--red)">-$420,000 <span style="font-size:12px;font-weight:normal">net cost</span></div>
              <table class="meta-table" style="font-size:11.5px">
                <tr><td>Ballast Steaming Time</td><td>14 Days</td></tr>
                <tr><td>Bunker Cost</td><td>-$420,000</td></tr>
                <tr><td>Backhaul Cargo</td><td>None (Pure Ballast)</td></tr>
                <tr><td>Idle Anchorage Time</td><td><span class="tag SHORT_TERM">2.0 Days</span></td></tr>
              </table>
              <button class="btn ghost small" style="margin-top:14px;width:100%;justify-content:center" disabled>Select Ballast</button>
            </div>

            <!-- Strategy 3: Short Spot Relet -->
            <div class="decision-card">
              <h4>3. Short Spot Relet</h4>
              <p style="font-size:12px;color:var(--ink-dim)">Relet vessel on 30-day spot charter to third-party operator in Bay of Bengal.</p>
              <div class="decision-cost" style="color:var(--blue)">+$64,000 <span style="font-size:12px;font-weight:normal">net earnings</span></div>
              <table class="meta-table" style="font-size:11.5px">
                <tr><td>Time Charter Rate</td><td>$18,500 / day</td></tr>
                <tr><td>Operator Margin</td><td>+$64,000 net</td></tr>
                <tr><td>Relet Term</td><td>25–35 Days</td></tr>
                <tr><td>Idle Anchorage Time</td><td><span class="tag HEALTHY">1.0 Days</span></td></tr>
              </table>
              <button class="btn ghost small" style="margin-top:14px;width:100%;justify-content:center">Explore Relet</button>
            </div>

          </div>
        </div>

        <!-- 7 East Coast Ports Demand Outlook Table -->
        <div class="panel">
          <h3>2–4 Week Demand Outlook Across All 7 East Coast Ports</h3>
          <div class="table-responsive">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Port Name</th>
                  <th>Region</th>
                  <th>2-Wk Forecast Cargo</th>
                  <th>Tonnage Outlook</th>
                  <th>Repositioning Rating</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><b>Paradip Port</b></td>
                  <td>Odisha</td>
                  <td>Iron Ore Export / Coal Import</td>
                  <td class="mono">280,000 MT</td>
                  <td><span class="tag HEALTHY">High Demand (Optimal)</span></td>
                </tr>
                <tr>
                  <td><b>Dhamra Port</b></td>
                  <td>Odisha</td>
                  <td>Thermal Coal Import</td>
                  <td class="mono">190,000 MT</td>
                  <td><span class="tag HEALTHY">Feasible</span></td>
                </tr>
                <tr>
                  <td><b>Visakhapatnam (Vizag)</b></td>
                  <td>Andhra Pradesh</td>
                  <td>Coking Coal Import</td>
                  <td class="mono">140,000 MT</td>
                  <td><span class="tag HEALTHY">Feasible</span></td>
                </tr>
                <tr>
                  <td><b>Gangavaram</b></td>
                  <td>Andhra Pradesh</td>
                  <td>Limestone / Coal</td>
                  <td class="mono">160,000 MT</td>
                  <td><span class="tag HEALTHY">Feasible</span></td>
                </tr>
                <tr>
                  <td><b>Gopalpur Port</b></td>
                  <td>Odisha</td>
                  <td>Ilmenite Sand Export</td>
                  <td class="mono">60,000 MT</td>
                  <td><span class="tag SHORT_TERM">Moderate</span></td>
                </tr>
                <tr>
                  <td><b>Haldia / Sagar</b></td>
                  <td>West Bengal</td>
                  <td>Thermal Coal / Fertilizer</td>
                  <td class="mono">85,000 MT</td>
                  <td><span class="tag SINGLE_SPOT">Lightering Only</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    `;

    container.querySelector('#btn-run-idle-advisor').addEventListener('click', () => {
      window.AppController?.showToast('Idle/Deadheading Advisor analyzed 7 ports. Backhaul Triangulation saves $97,500!', 'success');
    });

    container.querySelector('#btn-select-backhaul').addEventListener('click', () => {
      window.AppController?.showToast('Backhaul fixture confirmed (Paradip → Qingdao Iron Ore Pellets).', 'info');
    });
  }

  return { init };
})();
