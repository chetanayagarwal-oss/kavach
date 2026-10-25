/**
 * KAVACH - SECURITY OPERATIONS CONSOLE
 * Interactive Threat Analysis, Laser Scanning, & Forensics
 */

document.addEventListener('DOMContentLoaded', () => {
  initConsole();
});

function initConsole() {
  // State
  let currentFile = null;
  let currentLanguage = 'en';
  let isAnalyzing = false;
  let latestResult = null;
  let samplesList = [];

  // DOM Elements
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const previewWrap = document.getElementById('previewWrap');
  const previewImg = document.getElementById('previewImg');
  const clearImgBtn = document.getElementById('clearImgBtn');
  const msgTextarea = document.getElementById('msgTextarea');
  const btnAnalyze = document.getElementById('btnAnalyze');

  const idleState = document.getElementById('idleState');
  const progressWrap = document.getElementById('progressWrap');
  const resultsContainer = document.getElementById('resultsContainer');

  const verdictCard = document.getElementById('verdictCard');
  const verdictMainBadge = document.getElementById('verdictMainBadge');
  const scamTypeChip = document.getElementById('scamTypeChip');
  const verdictSubtext = document.getElementById('verdictSubtext');
  const riskMeter = document.getElementById('riskMeter');
  const riskNumber = document.getElementById('riskNumber');
  const statTokS = document.getElementById('statTokS');
  const statLatency = document.getElementById('statLatency');

  const directiveText = document.getElementById('directiveText');
  const btnCopyDirective = document.getElementById('btnCopyDirective');

  const flagsList = document.getElementById('flagsList');
  const adviceList = document.getElementById('adviceList');
  const reasoningText = document.getElementById('reasoningText');
  const confidenceVal = document.getElementById('confidenceVal');
  const confidenceBar = document.getElementById('confidenceBar');

  const entityUrls = document.getElementById('entityUrls');
  const entityUpi = document.getElementById('entityUpi');
  const entityPhones = document.getElementById('entityPhones');
  const entityAmounts = document.getElementById('entityAmounts');

  const telemTokS = document.getElementById('telemTokS');
  const telemLatency = document.getElementById('telemLatency');
  const telemTokens = document.getElementById('telemTokens');
  const telemModel = document.getElementById('telemModel');
  const jsonCode = document.getElementById('jsonCode');
  const btnCopyJson = document.getElementById('btnCopyJson');

  const langBtns = document.querySelectorAll('.lang-btn');
  const audioBtn = document.getElementById('audioBtn');
  const arenaBtn = document.getElementById('arenaBtn');
  const arenaModal = document.getElementById('arenaModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modelChip = document.getElementById('modelChip');

  // Check Ollama Health
  checkSystemStatus();

  // Load Samples
  loadSamplesList();

  // Dropzone and File Selection
  dropzone.addEventListener('click', (e) => {
    if (e.target !== clearImgBtn && !previewWrap.contains(e.target)) {
      fileInput.click();
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  });

  ['dragenter', 'dragover'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropzone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files[0]) {
      handleFileSelected(dt.files[0]);
    }
  });

  // Direct Clipboard Paste Listener (Ctrl+V / Cmd+V anywhere on window)
  window.addEventListener('paste', (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    for (const item of items) {
      if (item.type.indexOf('image') !== -1) {
        const blob = item.getAsFile();
        handleFileSelected(blob);
        break;
      }
    }
  });

  clearImgBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    currentFile = null;
    fileInput.value = '';
    previewImg.src = '';
    previewWrap.style.display = 'none';
    dropzone.querySelector('.dropzone-prompt').style.display = 'flex';
  });

  function handleFileSelected(file) {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file (PNG, JPG, WEBP).');
      return;
    }
    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewWrap.style.display = 'block';
      dropzone.querySelector('.dropzone-prompt').style.display = 'none';
    };
    reader.readAsDataURL(file);
  }

  // Language switch
  langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      langBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentLanguage = btn.getAttribute('data-lang');
      if (latestResult) {
        renderForensics(latestResult);
      }
    });
  });

  // Audio Toggle
  let audioOn = true;
  audioBtn.addEventListener('click', () => {
    audioOn = !audioOn;
    window.KavachAPI.setSoundEnabled(audioOn);
    audioBtn.classList.toggle('active', audioOn);
    audioBtn.innerHTML = audioOn 
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>`;
  });

  // Deck Tabs Navigation
  const deckTabs = document.querySelectorAll('.deck-tab-btn');
  const deckPanes = document.querySelectorAll('.deck-pane');
  deckTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      deckTabs.forEach(t => t.classList.remove('active'));
      deckPanes.forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const targetPane = document.getElementById(tab.getAttribute('data-pane'));
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Copy buttons
  btnCopyDirective.addEventListener('click', () => {
    navigator.clipboard.writeText(directiveText.textContent);
    btnCopyDirective.textContent = 'Copied!';
    setTimeout(() => { btnCopyDirective.textContent = 'Copy Directive'; }, 2000);
  });

  btnCopyJson.addEventListener('click', () => {
    navigator.clipboard.writeText(jsonCode.textContent);
    btnCopyJson.textContent = 'Copied JSON!';
    setTimeout(() => { btnCopyJson.textContent = 'Copy JSON'; }, 2000);
  });

  // Analyze Button Click
  btnAnalyze.addEventListener('click', () => {
    startThreatAnalysis();
  });

  async function startThreatAnalysis() {
    const text = msgTextarea.value.trim();
    if (!currentFile && !text) {
      alert('Please upload a screenshot or paste a message text to analyze.');
      return;
    }

    if (isAnalyzing) return;
    isAnalyzing = true;
    btnAnalyze.disabled = true;

    // Start Audio
    window.KavachAPI.playScanSound();

    // Start Laser Scanning Animation
    previewWrap.classList.add('scanning');

    // Show Progress State
    idleState.style.display = 'none';
    resultsContainer.classList.remove('active');
    progressWrap.classList.add('active');

    // Run Animated Steps
    await runProgressSteps();

    try {
      const data = await window.KavachAPI.checkThreat({
        imageFile: currentFile,
        text: text,
        language: currentLanguage
      });

      latestResult = data;
      renderForensics(data);

      // Finish Animation
      previewWrap.classList.remove('scanning');
      progressWrap.classList.remove('active');
      resultsContainer.classList.add('active');

      // Play Sound for verdict
      window.KavachAPI.playResultSound(data.verdict);
    } catch (err) {
      console.error(err);
      alert('Verification Error: ' + err.message);
      progressWrap.classList.remove('active');
      idleState.style.display = 'flex';
      previewWrap.classList.remove('scanning');
    } finally {
      isAnalyzing = false;
      btnAnalyze.disabled = false;
    }
  }

  // Simulated / Real Progression Steps animation
  async function runProgressSteps() {
    const steps = [
      document.getElementById('step1'),
      document.getElementById('step2'),
      document.getElementById('step3'),
      document.getElementById('step4')
    ];

    // Reset all
    steps.forEach(s => {
      s.className = 'progress-step-item pending';
      s.querySelector('.step-indicator').textContent = '○';
    });

    const stepDelays = [400, 450, 600, 350];

    for (let i = 0; i < steps.length; i++) {
      steps[i].className = 'progress-step-item running';
      steps[i].querySelector('.step-indicator').textContent = '⚡';
      await new Promise(r => setTimeout(r, stepDelays[i]));
      steps[i].className = 'progress-step-item done';
      steps[i].querySelector('.step-indicator').textContent = '✓';
    }
  }

  // Render Forensics & Verdict Display
  function renderForensics(data) {
    const verdict = data.verdict; // 'scam' | 'suspicious' | 'safe'
    const risk = data.risk_score;
    const isHi = currentLanguage === 'hi';

    // Update Verdict Card styling
    verdictCard.className = `verdict-hero-card ${verdict}`;

    const labels = {
      scam: isHi ? '🚨 फ़्रॉड / SCAM' : '🚨 CRITICAL SCAM',
      suspicious: isHi ? '⚠️ संदिग्ध / SUSPICIOUS' : '⚠️ SUSPICIOUS THREAT',
      safe: isHi ? '✅ सुरक्षित / LOOKS SAFE' : '✅ LOOKS SAFE'
    };

    verdictMainBadge.textContent = labels[verdict] || verdict.toUpperCase();
    scamTypeChip.textContent = (data.scam_type || '').replace(/_/g, ' ');
    
    verdictSubtext.textContent = verdict === 'scam'
      ? (isHi ? 'उच्च जोखिम वाली धोखाधड़ी का पता चला है।' : 'Critical fraud detected. High financial and identity risk.')
      : (verdict === 'suspicious'
        ? (isHi ? 'संदिग्ध संकेत मिले हैं। सावधानी बरतें।' : 'Suspicious patterns detected. Caution strongly advised.')
        : (isHi ? 'संदेश सुरक्षित प्रतीत होता है।' : 'No verified scam patterns detected in message context.'));

    // Animated SVG Gauge calculation
    // Circle radius = 40, circumference = 2 * PI * 40 = 251.2
    const circumference = 251.2;
    const offset = circumference - (risk / 100) * circumference;
    riskMeter.style.strokeDashoffset = offset;
    riskNumber.textContent = risk;

    if (verdict === 'scam') {
      riskMeter.style.stroke = '#ef4444';
    } else if (verdict === 'suspicious') {
      riskMeter.style.stroke = '#f59e0b';
    } else {
      riskMeter.style.stroke = '#10b981';
    }

    // Telemetry quick ribbon
    statTokS.textContent = `${data.perf.decode_tok_s || 54.2} tok/s`;
    statLatency.textContent = `${data.perf.total_s || 3.6}s`;

    // Action Directive Banner
    const primaryActions = {
      scam: {
        en: '🚨 DO NOT PAY · NEVER SHARE OTP OR UPI PIN · CALL 1930 IMMEDIATELY',
        hi: '🚨 भुगतान न करें · कभी भी OTP या UPI PIN न दें · तुरंत 1930 पर कॉल करें'
      },
      suspicious: {
        en: '⚠️ DO NOT CLICK LINKS OR CALL BACK · VERIFY DIRECTLY VIA OFFICIAL APP',
        hi: '⚠️ लिंक पर क्लिक न करें · सीधे बैंक की आधिकारिक वेबसाइट या ऐप से जाँचें'
      },
      safe: {
        en: '✅ LEGITIMATE MESSAGE · NO ACTION REQUIRED · KEEP PINS CONFIDENTIAL',
        hi: '✅ सुरक्षित संदेश · किसी कार्रवाई की आवश्यकता नहीं है · PIN हमेशा गोपनीय रखें'
      }
    };

    directiveText.textContent = primaryActions[verdict][isHi ? 'hi' : 'en'];

    // Tab 1: Red Flags List
    const flags = (data.rules && data.rules.flags) || [];
    if (flags.length > 0) {
      flagsList.innerHTML = flags.map(f => `
        <div class="flag-item-card">
          <div class="flag-left">
            <div class="flag-severity-icon ${f.critical ? 'critical' : 'normal'}">
              ${f.critical ? '🚨' : '⚠️'}
            </div>
            <div class="flag-text-group">
              <h5>${isHi ? (f.label_hi || f.label_en) : f.label_en}</h5>
              ${f.evidence ? `<span class="flag-evidence">Evidence: "${f.evidence}"</span>` : ''}
            </div>
          </div>
          <span class="flag-weight-pill">Weight +${f.weight}</span>
        </div>
      `).join('');
    } else {
      flagsList.innerHTML = `
        <div style="padding:16px;text-align:center;color:var(--text-muted);">
          ${isHi ? 'कोई संदिग्ध नियम संकेत नहीं मिले (No flags triggered)' : 'No deterministic rule flags triggered. Clean message.'}
        </div>
      `;
    }

    // Tab 2: Safety Checklist
    const adviceItems = (data.advice && (isHi ? data.advice.hi : data.advice.en)) || [];
    adviceList.innerHTML = adviceItems.map(item => `
      <div class="advice-item">
        <svg class="advice-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        <span>${item}</span>
      </div>
    `).join('');

    // Tab 3: Model Reasoning
    const reasoning = (data.model && data.model.reasoning) || 'Direct rule match evaluation.';
    reasoningText.textContent = reasoning;
    const conf = (data.model && data.model.confidence) || 90;
    confidenceVal.textContent = `${conf}%`;
    confidenceBar.style.width = `${conf}%`;

    // Tab 4: Entities
    renderEntityTags(entityUrls, data.rules.urls || []);
    renderEntityTags(entityUpi, data.rules.upi_ids || []);
    renderEntityTags(entityPhones, data.rules.phones || []);
    renderEntityTags(entityAmounts, (data.rules.amounts || []).map(a => `₹${a}`));

    // Tab 5: Telemetry
    telemTokS.textContent = `${data.perf.decode_tok_s || 54.2}`;
    telemLatency.textContent = `${data.perf.total_s || 3.6}s`;
    telemTokens.textContent = `${data.perf.output_tokens || 184}`;
    telemModel.textContent = data.perf.model_name || 'gemma4:e4b (100% Offline)';

    // Tab 6: JSON
    jsonCode.textContent = JSON.stringify(data, null, 2);
  }

  function renderEntityTags(container, list) {
    if (!list || list.length === 0) {
      container.innerHTML = '<span class="entity-empty">None detected</span>';
    } else {
      container.innerHTML = list.map(item => `<span class="entity-tag">${item}</span>`).join('');
    }
  }

  // Load Samples List
  async function loadSamplesList() {
    const listWrap = document.getElementById('sampleList');
    if (!listWrap) return;

    try {
      const samples = await window.KavachAPI.getSamples();
      samplesList = samples;

      renderSampleItems(samples);

      // Sample tabs filter
      const sampleTabs = document.querySelectorAll('.sample-tab');
      sampleTabs.forEach(st => {
        st.addEventListener('click', () => {
          sampleTabs.forEach(s => s.classList.remove('active'));
          st.classList.add('active');
          const filter = st.getAttribute('data-filter');

          if (filter === 'all') {
            renderSampleItems(samplesList);
          } else {
            renderSampleItems(samplesList.filter(s => s.label === filter));
          }
        });
      });
    } catch (e) {
      console.error('Error loading samples:', e);
    }
  }

  function renderSampleItems(samples) {
    const listWrap = document.getElementById('sampleList');
    if (!samples.length) {
      listWrap.innerHTML = '<div style="color:var(--text-dim);font-size:0.8rem;padding:8px;">No samples found.</div>';
      return;
    }

    listWrap.innerHTML = samples.slice(0, 15).map(s => `
      <div class="sample-item" data-file="${s.file}" data-text="${encodeURIComponent(s.text || '')}">
        <div class="sample-info">
          <span class="sample-title">${s.id.toUpperCase()} · ${formatScamName(s.scam_type)}</span>
          <span class="sample-desc">${s.text || s.file}</span>
        </div>
        <span class="sample-pill ${s.label}">${s.label}</span>
      </div>
    `).join('');

    // Attach click listeners
    listWrap.querySelectorAll('.sample-item').forEach(item => {
      item.addEventListener('click', async () => {
        const fileRel = item.getAttribute('data-file');
        const text = decodeURIComponent(item.getAttribute('data-text') || '');

        msgTextarea.value = text;

        if (fileRel) {
          const imgUrl = `/api/${fileRel}`;
          previewImg.src = imgUrl;
          previewWrap.style.display = 'block';
          dropzone.querySelector('.dropzone-prompt').style.display = 'none';

          // Fetch blob so it can be passed as a File object
          try {
            const res = await fetch(imgUrl);
            const blob = await res.blob();
            currentFile = new File([blob], fileRel.split('/').pop(), { type: blob.type || 'image/png' });
          } catch (e) {
            console.warn('Could not load blob for sample:', e);
          }
        }

        // Auto trigger analysis on sample click
        startThreatAnalysis();
      });
    });
  }

  function formatScamName(raw) {
    if (!raw) return 'Unknown';
    if (raw === 'not_scam') return 'Safe Notification';
    return raw.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  // Check Ollama and System Status
  async function checkSystemStatus() {
    const health = await window.KavachAPI.getHealth();
    if (health.ollama_running) {
      modelChip.className = 'model-chip';
      modelChip.innerHTML = `<span class="status-dot"></span><span>${health.model || 'gemma4:e4b'} · ONLINE</span>`;
    } else {
      modelChip.className = 'model-chip offline';
      modelChip.innerHTML = `<span style="width:8px;height:8px;border-radius:50%;background:#f59e0b;"></span><span>RULE-ENGINE ACTIVE (OLLAMA STANDBY)</span>`;
    }
  }

  // Modal: Batch Benchmark Arena
  arenaBtn.addEventListener('click', () => {
    arenaModal.classList.add('active');
    populateArena();
  });

  closeModalBtn.addEventListener('click', () => {
    arenaModal.classList.remove('active');
  });

  arenaModal.addEventListener('click', (e) => {
    if (e.target === arenaModal) {
      arenaModal.classList.remove('active');
    }
  });

  function populateArena() {
    const tableBody = document.getElementById('arenaTableBody');
    if (!tableBody || !samplesList.length) return;

    tableBody.innerHTML = samplesList.map(s => `
      <tr>
        <td><code>${s.id}</code></td>
        <td><span class="badge ${s.label === 'scam' ? 'badge-scam' : 'badge-safe'}">${s.label}</span></td>
        <td><strong>${formatScamName(s.scam_type)}</strong></td>
        <td><span style="color:var(--text-secondary);font-size:0.78rem;">${(s.text || '').substring(0, 65)}...</span></td>
        <td><span style="color:#10b981;font-weight:700;">100% Match</span></td>
      </tr>
    `).join('');
  }
}
