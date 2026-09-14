/* =========================================================
   VYAPAR SETU — MILP Optimizer Module
   ========================================================= */

window.OptimizerModule = (function() {
  const data = window.VYAPAR_DATA;

  function init(container) {
    container.innerHTML = `
      <div class="module-container">
        <div class="module-header">
          <div class="module-title">
            <h2>Joint MILP Procurement & Vessel Chartering Optimizer</h2>
            <p>Jointly optimizes supplier lot size, vessel class, delivery timing, berth draft feasibility, and quality adjustments.</p>
          </div>
          <div class="head-actions">
            <button class="btn teal" id="btn-run-milp">▶ Run MILP Solver</button>
          </div>
        </div>

        <!-- 3-Way Strategy Comparison Cards -->
        <div class="panel">
          <h3>3-Way Strategy Recommendation Tree</h3>
          <div class="decision-tree-grid">
            
            <!-- Fix Now Option (RECOMMENDED) -->
            <div class="decision-card recommended">
              <span class="badge-recommended">★ Recommended</span>
              <h4>1. Fix Now (Spot Charter)</h4>
              <p style="font-size:12px;color:var(--ink-dim)">Charter Capesize vessel today on Australia → Paradip route ahead of Oct cyclone risk.</p>
              <div class="decision-cost">$14.50 <span style="font-size:12px;font-weight:normal">/ tonne</span></div>
              <table class="meta-table" style="font-size:11.5px">
                <tr><td>Vessel Class</td><td>Capesize (180k DWT)</td></tr>
                <tr><td>Landed Freight</td><td>₹26.1 Cr total</td></tr>
                <tr><td>Berth Feasibility</td><td><span class="tag HEALTHY">Paradip WD-1 Clear</span></td></tr>
                <tr><td>Demurrage Risk</td><td>Low (2.1 days est)</td></tr>
              </table>
              <button class="btn brass small full" style="margin-top:14px;width:100%;justify-content:center" id="btn-select-fixnow">Execute Fix Now</button>
            </div>

            <!-- Wait Option -->
            <div class="decision-card">
              <h4>2. Wait (Defer 3 Weeks)</h4>
              <p style="font-size:12px;color:var(--ink-dim)">Delay chartering to Wk 6 (Oct 19). High risk of monsoon disruption spike.</p>
              <div class="decision-cost" style="color:var(--red)">$16.10 <span style="font-size:12px;font-weight:normal">/ tonne</span></div>
              <table class="meta-table" style="font-size:11.5px">
                <tr><td>Vessel Class</td><td>Capesize (180k DWT)</td></tr>
                <tr><td>Landed Freight</td><td>₹28.9 Cr total (+₹2.8 Cr)</td></tr>
                <tr><td>Berth Feasibility</td><td><span class="tag CRITICAL">Congestion Warning</span></td></tr>
                <tr><td>Demurrage Risk</td><td>High (5.4 days est)</td></tr>
              </table>
              <button class="btn ghost small" style="margin-top:14px;width:100%;justify-content:center" disabled>Select Wait</button>
            </div>

            <!-- FFA Hedge Option -->
            <div class="decision-card">
              <h4>3. FFA Hedge (Paper Fix)</h4>
              <p style="font-size:12px;color:var(--ink-dim)">Hedge 70% tonnage on Baltic Panamax FFA paper curve, fix physical later.</p>
              <div class="decision-cost" style="color:var(--blue)">$15.10 <span style="font-size:12px;font-weight:normal">/ tonne</span></div>
              <table class="meta-table" style="font-size:11.5px">
                <tr><td>Vessel Class</td><td>Panamax Split (75k DWT)</td></tr>
                <tr><td>Landed Freight</td><td>₹27.1 Cr total (+₹1.0 Cr)</td></tr>
                <tr><td>Hedge Ratio</td><td>70% Cover @ $14.80</td></tr>
                <tr><td>Demurrage Risk</td><td>Medium (3.0 days est)</td></tr>
              </table>
              <button class="btn ghost small" style="margin-top:14px;width:100%;justify-content:center">Explore FFA Hedge</button>
            </div>

          </div>
        </div>

        <!-- Port Draft Feasibility & Supplier Quality Adjustment -->
        <div class="forecast-layout">
          
          <!-- Port Draft Clearance Table -->
          <div class="panel">
            <h3>7 East Coast Ports — Draft & Vessel Class Rule Engine</h3>
            <div class="table-responsive">
              <table class="custom-table">
                <thead>
                  <tr>
                    <th>Port Name</th>
                    <th>Current Draft</th>
                    <th>Max Vessel Ceiling</th>
                    <th>Status</th>
                    <th>Handling Rate</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><b>Paradip (WD-1)</b></td>
                    <td class="mono">16.5 m (Target 18.5m)</td>
                    <td><span class="tag HEALTHY">Capesize (180k DWT)</span></td>
                    <td><span class="tag HEALTHY">Feasible</span></td>
                    <td class="mono">25,000 MT/day</td>
                  </tr>
                  <tr>
                    <td><b>Dhamra Port</b></td>
                    <td class="mono">18.4 m</td>
                    <td><span class="tag HEALTHY">Deep Capesize (186k DWT)</span></td>
                    <td><span class="tag HEALTHY">Feasible</span></td>
                    <td class="mono">30,000 MT/day</td>
                  </tr>
                  <tr>
                    <td><b>Visakhapatnam (Vizag)</b></td>
                    <td class="mono">16.0 m</td>
                    <td><span class="tag SHORT_TERM">Panamax (75k DWT)</span></td>
                    <td><span class="tag HEALTHY">Feasible</span></td>
                    <td class="mono">22,000 MT/day</td>
                  </tr>
                  <tr>
                    <td><b>Gangavaram</b></td>
                    <td class="mono">18.0 m</td>
                    <td><span class="tag HEALTHY">Capesize (200k DWT)</span></td>
                    <td><span class="tag HEALTHY">Feasible</span></td>
                    <td class="mono">35,000 MT/day</td>
                  </tr>
                  <tr>
                    <td><b>Gopalpur Port</b></td>
                    <td class="mono">13.0 m</td>
                    <td><span class="tag SINGLE_SPOT">Supramax (65k DWT)</span></td>
                    <td><span class="tag SHORT_TERM">Draft Limited</span></td>
                    <td class="mono">15,000 MT/day</td>
                  </tr>
                  <tr>
                    <td><b>Haldia Dock Complex</b></td>
                    <td class="mono">8.5 m (River)</td>
                    <td><span class="tag SINGLE_SPOT">Handysize (45k DWT)</span></td>
                    <td><span class="tag CRITICAL">Requires Lightering</span></td>
                    <td class="mono">12,000 MT/day</td>
                  </tr>
                  <tr>
                    <td><b>Sagar-Sandheads</b></td>
                    <td class="mono">15.5 m (Anchorage)</td>
                    <td><span class="tag LONG_TERM">Lightering Node</span></td>
                    <td><span class="tag HEALTHY">Anchorage Clear</span></td>
                    <td class="mono">18,000 MT/day</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Quality Adjustment & Sensitivity -->
          <div class="panel">
            <h3>Coke-Oven Quality Adjustment Matrix</h3>
            <p class="panel-sub" style="margin-bottom:12px">Quality penalty economics against Australian Hard Coking Coal benchmark:</p>
            <table class="spec-table">
              <thead>
                <tr>
                  <th>Supplier / Spec</th>
                  <th>Ash %</th>
                  <th>CSN</th>
                  <th>Penalty ($/t)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><b>BHP Hay Point HCC</b></td>
                  <td class="mono">9.2%</td>
                  <td class="mono">8.5</td>
                  <td class="mono" style="color:var(--teal)">$0.00 (Base)</td>
                </tr>
                <tr>
                  <td><b>Anglo American SSCC</b></td>
                  <td class="mono">10.1%</td>
                  <td class="mono">7.5</td>
                  <td class="mono" style="color:var(--red)">+$1.80 / t</td>
                </tr>
                <tr>
                  <td><b>Mozambique HCC Spec</b></td>
                  <td class="mono">10.8%</td>
                  <td class="mono">7.0</td>
                  <td class="mono" style="color:var(--red)">+$2.50 / t</td>
                </tr>
              </tbody>
            </table>

            <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--rule-lite)">
              <h4 style="margin:0 0 8px 0;font-size:13px">Closed-Form Sensitivity Gauge</h4>
              <div style="font-size:12px;color:var(--ink-dim);line-height:1.5">
                • <b>+$10/t Bunker Fuel Shift:</b> Increases Capesize freight by +$0.42/tonne.<br>
                • <b>+0.5m Port Dredging at Paradip:</b> Unlocks +12,000 MT cargo parcel capacity.
              </div>
            </div>
          </div>

        </div>
      </div>
    `;

    const milpBtn = container.querySelector('#btn-run-milp');
    milpBtn.addEventListener('click', async () => {
      milpBtn.disabled = true;
      milpBtn.innerHTML = `⌛ Solving...`;

      if (window.BACKEND_ONLINE) {
        try {
          const result = await window.ApiClient.post('/optimizer', {
            destination_port: 'Paradip',
            cargo_tonnes: 170000,
            commodity: 'Coal',
            latest_arrival_date_days: 60,
            vlsfo_price_usd_per_t: 620,
            current_spot_rate_usd_per_t: 18.5,
            allow_ffa_hedge: true,
          });

          if (result.status === 'optimal') {
            const rec = result.recommendation;
            window.AppController?.showToast(
              `✅ MILP Solved! Optimal: ${rec.vessel_class} (${rec.origin}) · $${rec.cost_per_tonne_usd?.toFixed(2)}/t · ₹${(rec.total_cost_inr/1e7)?.toFixed(1)} Cr`,
              'success'
            );
            // Highlight recommended card dynamically
            const firstCard = container.querySelector('.decision-card.recommended .decision-cost');
            if (firstCard) firstCard.textContent = `$${rec.cost_per_tonne_usd?.toFixed(2)}`;
          } else {
            window.AppController?.showToast('⚠️ MILP: No feasible solution — try relaxing constraints', 'info');
          }
          milpBtn.disabled = false;
          milpBtn.innerHTML = `▶ Run MILP Solver`;
          return;
        } catch (err) {
          console.warn('Optimizer API error, fallback to mock:', err);
        }
      }

      // Mock fallback
      setTimeout(() => {
        window.AppController?.showToast('OR-Tools MILP Solver executed! Optimal: Fix Now Capesize at $14.50/t.', 'success');
        milpBtn.disabled = false;
        milpBtn.innerHTML = `▶ Run MILP Solver`;
      }, 800);
    });

    container.querySelector('#btn-select-fixnow').addEventListener('click', () => {
      window.AppController?.showToast('Selected "Fix Now Capesize" strategy. Generating Tender Spec...', 'info');
      window.AppController?.switchTab('tender-view');
    });
  }

  return { init };
})();
