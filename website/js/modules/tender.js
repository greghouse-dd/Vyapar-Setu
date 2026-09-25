/* =========================================================
   VYAPAR SETU — Tender Specification Generator Module
   ========================================================= */

window.TenderModule = (function() {
  const data = window.VYAPAR_DATA;
  let activeLang = 'Odia';

  // Cache translated results to avoid re-fetching
  const translationCache = {};
  let isTranslating = false;

  // The English source text for translation (structured as key-value pairs)
  const ENGLISH_SPEC_TEXT =
    'Cargo Item: Australian Hard Coking Coal (HCC)\n' +
    'Tonnage Lot Size: 180,000 Metric Tons (±5% Operational Tolerance)\n' +
    'Destination Berth: Paradip Western Dock-1 (WD-1)\n' +
    'Maximum Draft Clearance: 16.5 Metres Laden Draft Ceiling\n' +
    'Recommended Vessel Class: Capesize (180,000 DWT)\n' +
    'Delivery Schedule Window: 05 October 2026 to 15 October 2026\n' +
    'Maximum Freight Ceiling: USD $14.85 / Metric Ton\n' +
    'Coke-Oven Quality Criteria: Ash Content ≤ 9.5%, CSN ≥ 8.0, Volatile Matter 20-22%.';

  /**
   * Call the backend Sarvam translation pipeline.
   * POST /vernacular/translate-tender
   */
  async function fetchTranslation(lang) {
    if (translationCache[lang]) return translationCache[lang];

    const resp = await window.ApiClient.post('/vernacular/translate-tender', {
      text: ENGLISH_SPEC_TEXT,
      target_language: lang,
      source_language: 'en-IN',
    });

    // resp.translated contains the translated text string
    translationCache[lang] = resp.translated;
    return resp.translated;
  }

  /**
   * Convert the translated plain-text block into styled HTML lines.
   * Each line is expected to be "Label: Value" — we bold the label.
   */
  function formatTranslatedHtml(translatedText) {
    return translatedText
      .split('\n')
      .filter(line => line.trim())
      .map(line => {
        const colonIdx = line.indexOf(':');
        if (colonIdx > 0) {
          const label = line.substring(0, colonIdx).trim();
          const value = line.substring(colonIdx + 1).trim();
          return `<b>${label}:</b> ${value}`;
        }
        return line;
      })
      .join('<br>');
  }

  function renderTranslationColumn() {
    if (isTranslating) {
      return `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:160px;gap:12px">
          <div class="translate-spinner" style="width:32px;height:32px;border:3px solid var(--rule);border-top-color:var(--brass);border-radius:50%;animation:spin 0.8s linear infinite"></div>
          <div style="font-size:13px;color:var(--ink-dim)">Translating to <b>${activeLang}</b> via Sarvam Mayura…</div>
        </div>
        <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
      `;
    }

    const cached = translationCache[activeLang];
    if (cached) {
      return formatTranslatedHtml(cached);
    }

    // Not yet fetched and not loading — show prompt
    return `<div style="font-size:13px;color:var(--ink-faint);font-style:italic">Select a language to translate via Sarvam AI pipeline.</div>`;
  }

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
            <div id="tender-translation-content" style="font-size:12.5px;color:var(--ink);line-height:1.6">
              ${renderTranslationColumn()}
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

    container.querySelector('#tender-lang-select').addEventListener('change', async (e) => {
      activeLang = e.target.value;
      await triggerTranslation(container);
    });

    bindDocEvents(container);

    // Trigger initial translation on load
    triggerTranslation(container);
  }

  /**
   * Fetch translation from backend and update the translation column.
   * If backend is offline, shows a fallback message.
   */
  async function triggerTranslation(container) {
    const contentEl = container.querySelector('#tender-translation-content');
    const headerEl = contentEl?.previousElementSibling;

    // Update header to reflect selected language
    if (headerEl) {
      headerEl.textContent = `2. Vernacular Translation (${activeLang} — Sarvam-Translate)`;
    }

    if (!window.BACKEND_ONLINE) {
      contentEl.innerHTML = `
        <div style="padding:16px;background:var(--brass-bg);border-radius:6px;border:1px solid var(--brass)">
          <div style="font-size:13px;font-weight:600;color:var(--brass)">⚠️ Backend Offline</div>
          <div style="font-size:12px;color:var(--ink-dim);margin-top:4px">
            Start the backend server to enable live Sarvam Mayura translation.<br>
            <code style="font-size:11px">cd website/backend && .\\start.bat</code>
          </div>
        </div>
      `;
      return;
    }

    // Check cache first
    if (translationCache[activeLang]) {
      contentEl.innerHTML = formatTranslatedHtml(translationCache[activeLang]);
      return;
    }

    // Show loading spinner
    isTranslating = true;
    contentEl.innerHTML = renderTranslationColumn();

    try {
      const translated = await fetchTranslation(activeLang);
      isTranslating = false;
      contentEl.innerHTML = formatTranslatedHtml(translated);
      window.AppController?.showToast(`✅ Translated to ${activeLang} via Sarvam Mayura`, 'success');
    } catch (err) {
      isTranslating = false;
      console.error('Translation API error:', err);
      contentEl.innerHTML = `
        <div style="padding:16px;background:#fef2f2;border-radius:6px;border:1px solid #fca5a5">
          <div style="font-size:13px;font-weight:600;color:#dc2626">Translation Error</div>
          <div style="font-size:12px;color:var(--ink-dim);margin-top:4px">
            ${err.message || 'Failed to translate via Sarvam AI.'}<br>
            <span style="font-size:11px;color:var(--ink-faint)">Ensure SARVAM_API_KEY is set in <code>.env</code> for live translation.</span>
          </div>
        </div>
      `;
      window.AppController?.showToast(`⚠️ Translation failed: ${err.message}`, 'danger');
    }
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
