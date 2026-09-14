/* =========================================================
   VYAPAR SETU — Sarvam AI Vernacular Copilot Module
   ========================================================= */

window.VernacularModule = (function() {
  const data = window.VYAPAR_DATA;
  let activeLang = 'hi';
  let isRecording = false;

  function renderVoiceCard(sample) {
    return `
      <div class="voice-copilot-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <div class="sarvam-badge">
            ⚡ Powered by Sarvam AI · Saaras (STT) + Bulbul (TTS) + Sarvam-Translate
          </div>
          <div style="display:flex;gap:6px">
            <button class="btn ${activeLang==='hi'?'brass':'ghost'} small" data-lang="hi">Hindi 🇮🇳</button>
            <button class="btn ${activeLang==='or'?'brass':'ghost'} small" data-lang="or">Odia 🇮🇳</button>
            <button class="btn ${activeLang==='te'?'brass':'ghost'} small" data-lang="te">Telugu 🇮🇳</button>
            <button class="btn ${activeLang==='bn'?'brass':'ghost'} small" data-lang="bn">Bengali 🇮🇳</button>
          </div>
        </div>

        <div class="voice-mic-container">
          <button class="mic-btn-large ${isRecording ? 'recording' : ''}" id="btn-mic-trigger">
            🎙️
          </button>
          <div style="text-align:center">
            <div style="font-size:15px;font-weight:600;color:var(--ink)" id="mic-status-heading">
              ${isRecording ? 'Listening via Sarvam Saaras...' : 'Click microphone to ask in ' + sample.lang}
            </div>
            <div style="font-size:12.5px;color:var(--ink-dim);margin-top:4px" id="mic-status-sub">
              "${sample.audioText}"
            </div>
          </div>
          ${isRecording ? `
            <div class="soundwave-anim">
              <span></span><span></span><span></span><span></span><span></span>
            </div>
          ` : ''}
        </div>

        <!-- Voice Query Result Panel -->
        <div id="voice-result-box" class="panel" style="margin-bottom:0;background:var(--card)">
          <h3>Sarvam AI Audio Synthesis & Rationale Output</h3>
          
          <div style="margin-bottom:14px">
            <div style="font-size:11px;color:var(--ink-faint);text-transform:uppercase;font-weight:600">Speech-To-Text (Saaras Transcription):</div>
            <div style="font-size:13.5px;font-style:italic;color:var(--ink);margin-top:2px">"${sample.transcription}"</div>
            <div style="font-size:11.5px;color:var(--ink-dim);margin-top:2px">English Translation: "${sample.translatedEn}"</div>
          </div>

          <div style="padding:14px;background:var(--brass-bg);border-radius:4px;border:1px solid var(--brass);margin-bottom:14px">
            <div style="font-size:11px;color:var(--brass);font-weight:600;text-transform:uppercase">Spoken Response (Bulbul TTS Audio Synthesis):</div>
            <div style="font-size:14px;font-weight:500;color:var(--ink);margin-top:4px">"${sample['response' + sample.lang.substring(0,2)]}"</div>
            <div style="font-size:12px;color:var(--ink-dim);margin-top:4px">English Summary: "${sample.responseEn}"</div>
            
            <button class="btn brass small" style="margin-top:10px" id="btn-play-audio">
              🔊 Play Spoken Audio Response (${sample.lang})
            </button>
          </div>

          <div style="font-size:11.5px;color:var(--ink-faint)">
            <b>SHAP Rationale Drivers:</b> ${sample.shapSummary}
          </div>
        </div>

      </div>
    `;
  }

  function init(container) {
    const sample = data.SARVAM_VOICE_SAMPLES[activeLang];

    container.innerHTML = `
      <div class="module-container">
        <div class="module-header">
          <div class="module-title">
            <h2>Vernacular AI Copilot & Voice Ingestion (Sarvam AI Integration)</h2>
            <p>Sovereign Indian speech-to-text, text-to-speech, and regional translation layer in Hindi, Odia, Telugu, and Bengali.</p>
          </div>
          <div class="head-actions">
            <button class="btn brass" id="btn-gen-vernacular-tender">📑 Vernacular Tender Spec</button>
          </div>
        </div>

        <div id="voice-card-wrap">
          ${renderVoiceCard(sample)}
        </div>

        <!-- Field Agent Voice Note Ingestion Panel -->
        <div class="panel">
          <h3>Voice-Note Field Congestion Ingestion (Field Agents Feed)</h3>
          <p class="panel-sub" style="margin-bottom:14px">Converts field agents' berth congestion voice notes into structured port wait-time features:</p>

          <div class="table-responsive">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>Field Agent</th>
                  <th>Port Location</th>
                  <th>Language</th>
                  <th>Voice Note Audio Snippet</th>
                  <th>Extracted Congestion Signal</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><b>Subhash Swain</b></td>
                  <td>Paradip (Odisha)</td>
                  <td>Odia</td>
                  <td><i>"Paradip WD-1 re 2 din delay aachi, mausam kharab..."</i></td>
                  <td><span class="tag CRITICAL">+2.0 Days Berth Delay</span></td>
                  <td class="mono" style="color:var(--teal)">98.4% (Saaras)</td>
                </tr>
                <tr>
                  <td><b>Ramu Reddy</b></td>
                  <td>Vizag Port (AP)</td>
                  <td>Telugu</td>
                  <td><i>"Vizag berth clearance normal undi, 1 day wait..."</i></td>
                  <td><span class="tag HEALTHY">+1.0 Day Wait</span></td>
                  <td class="mono" style="color:var(--teal)">97.1% (Saaras)</td>
                </tr>
                <tr>
                  <td><b>Arup Banerjee</b></td>
                  <td>Haldia Dock (WB)</td>
                  <td>Bengali</td>
                  <td><i>"Haldia river draft river silt barche, lightering dorkar..."</i></td>
                  <td><span class="tag SHORT_TERM">Draft Constraint Alert</span></td>
                  <td class="mono" style="color:var(--teal)">96.5% (Saaras)</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    `;

    bindEvents(container);
  }

  function bindEvents(container) {
    const wrap = container.querySelector('#voice-card-wrap');

    wrap.querySelectorAll('[data-lang]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        activeLang = e.target.dataset.lang;
        wrap.innerHTML = renderVoiceCard(data.SARVAM_VOICE_SAMPLES[activeLang]);
        bindVoiceControls(container);
      });
    });

    bindVoiceControls(container);

    container.querySelector('#btn-gen-vernacular-tender').addEventListener('click', () => {
      window.AppController?.switchTab('tender-view');
    });
  }

  function bindVoiceControls(container) {
    const micBtn = container.querySelector('#btn-mic-trigger');
    const playBtn = container.querySelector('#btn-play-audio');

    micBtn?.addEventListener('click', () => {
      isRecording = !isRecording;
      const sample = data.SARVAM_VOICE_SAMPLES[activeLang];
      container.querySelector('#voice-card-wrap').innerHTML = renderVoiceCard(sample);
      bindEvents(container);

      if (isRecording) {
        window.AppController?.showToast(`Listening in ${sample.lang}... Speak your question.`, 'info');
        setTimeout(() => {
          isRecording = false;
          container.querySelector('#voice-card-wrap').innerHTML = renderVoiceCard(sample);
          bindEvents(container);
          window.AppController?.showToast(`Transcribed via Sarvam Saaras! Audio answer generated.`, 'success');
        }, 2200);
      }
    });

    playBtn?.addEventListener('click', () => {
      const sample = data.SARVAM_VOICE_SAMPLES[activeLang];
      
      // Browser SpeechSynthesis fallback audio playback
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const textToSpeak = sample['response' + sample.lang.substring(0,2)];
        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
      }
      
      window.AppController?.showToast(`Playing spoken response via Sarvam Bulbul (${sample.lang})...`, 'success');
    });
  }

  return { init };
})();
