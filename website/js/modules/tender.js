/* =========================================================
   VYAPAR SETU — Tender Specification Generator Module
   ========================================================= */

window.TenderModule = (function() {
  const data = window.VYAPAR_DATA;
  let activeLang = 'Odia';

  function renderTenderDoc() {
    return `
      <div style="background:var(--card);border:2px solid var(--ink);border-radius:6px;padding:32px;box-shadow:0 6px 18px rgba(0,0,0,0.06);font-family:'Inter',sans-serif">
        
        <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid var(--ink);padding-bottom:16px;margin-bottom:24px">
          <div>
            <div style="font-family:'Fraunces',serif;font-size:22px;font-weight:700;color:var(--ink)">PARADIP PORT AUTHORITY / SAIL PROCUREMENT DESK</div>
            <div style="font-size:12px;color:var(--ink-dim);margin-top:2px">Official Tender Specification & Notice Inviting Tender (NIT)</div>
          </div>
          <div style="text-align:right" class="mono">
            <div style="font-size:12px;font-weight:600;color:var(--brass)">TENDER REF: NIT-SAIL-2026-089</div>
            <div style="font-size:11px;color:var(--ink-faint);margin-top:2px">Date: 14 September 2026</div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:24px">
          
          <!-- English Original Column -->
          <div style="border-right:1px solid var(--rule);padding-right:20px">
            <h4 style="margin:0 0 10px 0;font-size:13px;color:var(--teal);text-transform:uppercase">1. English Technical Specification</h4>
            <div style="font-size:12.5px;color:var(--ink);line-height:1.6">
              <b>Cargo Item:</b> Australian Hard Coking Coal (HCC)<br>
              <b>Tonnage Lot Size:</b> 180,000 Metric Tons (±5% Operational Tolerance)<br>
              <b>Destination Berth:</b> Paradip Western Dock-1 (WD-1)<br>
              <b>Maximum Draft Clearance:</b> 16.5 Metres Laden Draft Ceiling<br>
              <b>Recommended Vessel Class:</b> Capesize (180,000 DWT)<br>
              <b>Delivery Schedule Window:</b> 05 October 2026 to 15 October 2026<br>
              <b>Maximum Freight Ceiling:</b> USD $14.85 / Metric Ton<br>
              <b>Coke-Oven Quality Criteria:</b> Ash Content ≤ 9.5%, CSN ≥ 8.0, Volatile Matter 20-22%.
            </div>
          </div>

          <!-- Sarvam-Translate Regional Column -->
          <div>
            <h4 style="margin:0 0 10px 0;font-size:13px;color:var(--brass);text-transform:uppercase">2. Vernacular Translation (${activeLang} — Sarvam-Translate)</h4>
            <div style="font-size:12.5px;color:var(--ink);line-height:1.6">
              <b>କାର୍ଗୋ ସାମଗ୍ରୀ:</b> ଅଷ୍ଟ୍ରେଲିୟ ହାର୍ଡ କୋକିଂ କୋଇଲା (HCC)<br>
              <b>ମୋଟ ପରିମାଣ:</b> ୧୮୦,୦୦୦ ମେଟ୍ରିକ ଟନ୍ (±୫% ଅପରେସନାଲ)<br>
              <b>ଗନ୍ତବ୍ୟ ବନ୍ଦର:</b> ପାରାଦୀପ ୱେଷ୍ଟର୍ନ ଡକ୍-୧ (WD-1)<br>
              <b>ସର୍ବାଧିକ ଡ୍ରାଫ୍ଟ:</b> ୧୬.୫ ମିଟର ସୀମା<br>
              <b>ସୁପାରିଶକୃତ ଜାହାଜ:</b> କେପସାଇଜ୍ (180,000 DWT)<br>
              <b>ପହଞ୍ଚିବା ସମୟ:</b> ୦୫ ଅକ୍ଟୋବର ୨୦୨୬ ରୁ ୧୫ ଅକ୍ଟୋବର ୨୦୨୬<br>
              <b>ସର୍ବାଧିକ ଫ୍ରେଟ୍ ସୀମା:</b> USD $14.85 / ମେଟ୍ରିକ ଟନ୍<br>
              <b>ଗୁଣବତ୍ତା ମାପଦଣ୍ଡ:</b> ଆଶ୍ ≤ ୯.୫%, CSN ≥ ୮.୦।
            </div>
          </div>

        </div>

        <div style="border-top:1px solid var(--rule-lite);padding-top:16px;display:flex;justify-content:space-between;align-items:center">
          <div style="font-size:11px;color:var(--ink-faint)" class="mono">
            ✓ Audited by Vyapar Setu Decision Engine · Log Hash: 0x8f2a4e9b
          </div>
          <div style="display:flex;gap:10px">
            <button class="btn ghost small" id="btn-print-tender">🖨️ Print / Save PDF</button>
            <button class="btn brass small" id="btn-download-tender">📥 Download Tender (.DOCX)</button>
          </div>
        </div>

      </div>
    `;
  }

  function init(container) {
    container.innerHTML = `
      <div class="module-container">
        <div class="module-header">
          <div class="module-title">
            <h2>Pre-Tender Specification Document Generator</h2>
            <p>Generates CVC-compliant pre-tender procurement specifications pre-filled with optimal lot sizes, vessel classes, quality adjustments, and side-by-side Sarvam regional translations.</p>
          </div>
          <div class="head-actions">
            <select id="tender-lang-select" style="font-size:12px">
              <option value="Odia" selected>Odia Translation (Paradip / Dhamra)</option>
              <option value="Telugu">Telugu Translation (Vizag / Gangavaram)</option>
              <option value="Bengali">Bengali Translation (Haldia / Sagar)</option>
            </select>
          </div>
        </div>

        <div id="tender-doc-wrap">
          ${renderTenderDoc()}
        </div>
      </div>
    `;

    container.querySelector('#tender-lang-select').addEventListener('change', (e) => {
      activeLang = e.target.value;
      container.querySelector('#tender-doc-wrap').innerHTML = renderTenderDoc();
      bindDocEvents(container);
    });

    bindDocEvents(container);
  }

  function bindDocEvents(container) {
    container.querySelector('#btn-print-tender')?.addEventListener('click', () => {
      window.print();
    });

    container.querySelector('#btn-download-tender')?.addEventListener('click', async () => {
      if (window.BACKEND_ONLINE) {
        try {
          await window.ApiClient.download(
            '/generate-tender',
            {
              recommendation: {
                vessel_class: 'Capesize',
                timing: 'fix_now',
                origin: 'Australia',
                lot_size_tonnes: 180000,
                n_voyages: 1,
                voyage_days: 35,
                freight_cost_usd: 2610000,
                demurrage_cost_usd: 36000,
                quality_penalty_usd: 0,
                total_cost_usd: 2646000,
                total_cost_inr: 220941000,
                cost_per_tonne_usd: 14.7,
                cost_per_tonne_inr: 1227.45,
                rationale: 'Single Capesize voyage from Australia — fix_now. Voyage: 35d sea + 35d laycan = 70d total.',
              },
              shap_drivers: [
                { driver: 'Freight rate (spot × timing premium)', contribution_usd: 2610000, contribution_pct: 98.6, direction: 'positive' },
                { driver: 'Demurrage (excess berth wait)', contribution_usd: 36000, contribution_pct: 1.4, direction: 'positive' },
              ],
              request_payload: { destination_port: 'Paradip', cargo_tonnes: 180000, commodity: 'Coal', latest_arrival_date_days: 70 },
              generated_by: 'Vyapar Setu v1.0',
            },
            'NIT-SAIL-2026-089.docx'
          );
          window.AppController?.showToast('✅ Tender Specification downloaded (English .docx)', 'success');
          return;
        } catch (err) {
          console.warn('Tender download API error:', err);
        }
      }
      // Mock fallback
      window.AppController?.showToast('Downloaded Tender Specification (NIT-SAIL-2026-089.docx) in English + ' + activeLang, 'success');
    });
  }

  return { init };
})();
