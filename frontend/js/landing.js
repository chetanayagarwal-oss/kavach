/**
 * KAVACH - LANDING PAGE INTERACTIONS
 */

document.addEventListener('DOMContentLoaded', () => {
  initHeroSimulator();
  initThreatTabs();
  initFaqAccordion();
  initStatCounters();
});

// Interactive Hero Mini-Scanner Simulator
function initHeroSimulator() {
  const textarea = document.getElementById('heroSimInput');
  const chips = document.querySelectorAll('.sim-chip');
  const verdictCard = document.getElementById('heroSimCard');
  const verdictTitle = document.getElementById('heroSimVerdict');
  const riskPill = document.getElementById('heroSimRisk');
  const actionText = document.getElementById('heroSimAction');
  const flagsList = document.getElementById('heroSimFlags');

  if (!textarea || !chips.length) return;

  const presets = {
    sbi: {
      text: 'Dear customer your SBI account will be blocked today. Update PAN immediately: http://sbi-kyc-verify.top/login',
      verdict: '🚨 HIGH RISK SCAM / फ़्रॉड',
      risk: 'Risk 83/100',
      action: '🚨 DO NOT CLICK LINKS · Bank never asks for PAN updates via random websites · Report to 1930',
      isSafe: false,
    },
    upi: {
      text: 'refund.desk@okfake has requested Rs 4,999. Approve the request and enter UPI PIN to receive your cashback of Rs 4,999.',
      verdict: '🚨 CRITICAL UPI FRAUD / फ़्रॉड',
      risk: 'Risk 95/100',
      action: '🚨 NEVER ENTER UPI PIN TO RECEIVE MONEY · Entering PIN always DEDUCTS money from your account',
      isSafe: false,
    },
    safe: {
      text: 'Your package with Boat headphones will be delivered today by 9 pm. Track: amazon.in/your-orders',
      verdict: '✅ LOOKS SAFE / सुरक्षित',
      risk: 'Risk 0/100',
      action: '✅ Legitimate delivery notification · Official domain amazon.in verified · No financial risk',
      isSafe: true,
    }
  };

  // Click chips
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const key = chip.getAttribute('data-preset');
      const preset = presets[key];
      if (!preset) return;

      textarea.value = preset.text;
      updateSimulatorUI(preset);
    });
  });

  // Debounced input handler
  let debounceTimer;
  textarea.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      const txt = textarea.value.trim();
      if (!txt) return;

      if (window.KavachAPI) {
        const ruleData = await window.KavachAPI.quickRuleCheck(txt);
        if (ruleData) {
          const isScam = ruleData.score >= 50 || ruleData.has_critical;
          updateSimulatorUI({
            verdict: isScam ? '🚨 SCAM / फ़्रॉड DETECTED' : (ruleData.score >= 30 ? '⚠️ SUSPICIOUS / संदिग्ध' : '✅ LOOKS SAFE / सुरक्षित'),
            risk: `Risk ${ruleData.score}/100`,
            action: isScam 
              ? '🚨 SUSPICIOUS FINANCIAL SIGNALS DETECTED · Do not share OTP/PIN or transfer money' 
              : '✅ No immediate critical scam indicators triggered.',
            isSafe: !isScam,
          });
        }
      }
    }, 300);
  });

  function updateSimulatorUI(p) {
    if (p.isSafe) {
      verdictCard.classList.add('safe');
    } else {
      verdictCard.classList.remove('safe');
    }
    verdictTitle.textContent = p.verdict;
    riskPill.textContent = p.risk;
    actionText.textContent = p.action;
    
    // Play light sound
    if (window.KavachAPI) {
      window.KavachAPI.playResultSound(p.isSafe ? 'safe' : 'scam');
    }
  }
}

// 6 Core Scam Threat Showcase Tabs
function initThreatTabs() {
  const tabs = document.querySelectorAll('.threat-tab-btn');
  const displayTitle = document.getElementById('threatTitle');
  const displayDesc = document.getElementById('threatDesc');
  const displayImg = document.getElementById('threatImg');
  const displayFlags = document.getElementById('threatFlags');
  const displayAction = document.getElementById('threatAction');

  if (!tabs.length || !displayTitle) return;

  const threatData = {
    'digital-arrest': {
      title: 'Digital Arrest & Law Enforcement Impersonation',
      desc: 'Fraudsters impersonate CBI, Mumbai Police, or TRAI officers via Skype/WhatsApp video calls claiming drugs were found in a courier parcel in your name. They enforce fake "digital arrest" and demand emergency money transfers.',
      img: '/api/samples/s01.png',
      flags: [
        'Threatens immediate arrest warrant or police custody',
        'Instructs victim to "Stay on video call" and not inform family',
        'Official Indian police never conduct investigations or bail via Skype/WhatsApp'
      ],
      action: 'IMMEDIATE ACTION: Hang up instantly. Police cannot place you under "digital arrest". Dial 1930 immediately.'
    },
    'upi-collect': {
      title: 'UPI Collect & Fake Cashback Trap',
      desc: 'Scammers send a UPI Collect Request disguised as "Cashback", "Diwali Bonus", or "Refund", instructing victims to enter their UPI PIN to accept money.',
      img: '/api/samples/s03.png',
      flags: [
        'Demands UPI PIN entry to "receive" funds (PIN is ONLY used to SEND money)',
        'Suspicious VPA address (e.g. refund.desk@okfake)',
        'Manufactured urgency regarding expiring bonus'
      ],
      action: 'IMMEDIATE ACTION: Decline the collect request. NEVER enter UPI PIN to receive money.'
    },
    'kyc-freeze': {
      title: 'Fake Bank & SIM KYC Suspension Phishing',
      desc: 'SMS messages claiming your SBI/HDFC bank account or SIM card will be deactivated unless you update your PAN or Aadhaar via an unverified link.',
      img: '/api/samples/s02.png',
      flags: [
        'Sent from non-standard SMS header or random mobile number',
        'Phishing domain impersonation (e.g. sbi-kyc-verify.top)',
        'Deadline threat: "account will be blocked today"'
      ],
      action: 'IMMEDIATE ACTION: Never tap the link. Banks never send third-party domains for PAN updates. Verify only inside official bank apps.'
    },
    'electricity': {
      title: 'Electricity Bill Disconnection Panic',
      desc: 'SMS sent in the evening stating electricity supply will be severed at 9:30 PM due to unpaid bill, prompting immediate call to a personal fraudster number.',
      img: '/api/samples/s05.png',
      flags: [
        'Calls personal 10-digit mobile number instead of official power discom',
        'Short-fused cutoff deadline (e.g. "tonight at 9:30 pm")',
        'Fake official authority impersonation'
      ],
      action: 'IMMEDIATE ACTION: Do not call the number. Check bill status on your electricity board\'s official consumer portal.'
    },
    'job-tasks': {
      title: 'Part-Time Task & Telegram Pre-Paid Scam',
      desc: 'Offers of earning ₹3,000–₹5,000 daily by simply liking YouTube videos or reviewing hotels on Google Maps. Starts with small payouts, then requires "prepaid task deposits".',
      img: '/api/samples/s06.png',
      flags: [
        'Guaranteed daily returns for trivial tasks',
        'Redirects conversation to anonymous Telegram task groups',
        'Requests "prepaid deposit" to unlock higher commission'
      ],
      action: 'IMMEDIATE ACTION: Exit and block the group. Legitimate jobs never ask employees to pay advance money.'
    },
    'anydesk-apk': {
      title: 'AnyDesk Remote Access & Malicious APKs',
      desc: 'Victims are asked to install screen-sharing software (AnyDesk, TeamViewer QuickSupport) or sideload `.apk` files from unknown links under the guise of customer support.',
      img: '/api/samples/s11.png',
      flags: [
        'Asks to install AnyDesk/TeamViewer or share a 9-digit access code',
        'Requests installation of unverified `.apk` packages',
        'Allows attacker complete screen and OTP visibility'
      ],
      action: 'IMMEDIATE ACTION: Never share remote desktop codes. Delete downloaded APK files immediately and restart device in safe mode.'
    }
  };

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const key = tab.getAttribute('data-threat');
      const data = threatData[key];
      if (!data) return;

      displayTitle.textContent = data.title;
      displayDesc.textContent = data.desc;
      displayImg.src = data.img;
      displayAction.textContent = data.action;

      displayFlags.innerHTML = data.flags.map(f => `
        <li>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          <span>${f}</span>
        </li>
      `).join('');
    });
  });
}

// FAQ Accordion
function initFaqAccordion() {
  const items = document.querySelectorAll('.faq-item');
  items.forEach(item => {
    const question = item.querySelector('.faq-question');
    question.addEventListener('click', () => {
      const isActive = item.classList.contains('active');
      items.forEach(i => i.classList.remove('active'));
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
}

// Animated Statistic Counters
function initStatCounters() {
  const counters = document.querySelectorAll('.stat-value[data-target]');
  if (!counters.length) return;

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseFloat(el.getAttribute('data-target'));
        const prefix = el.getAttribute('data-prefix') || '';
        const suffix = el.getAttribute('data-suffix') || '';
        const isDecimal = target % 1 !== 0;

        let current = 0;
        const duration = 1600;
        const steps = 40;
        const inc = target / steps;
        const stepTime = duration / steps;

        const timer = setInterval(() => {
          current += inc;
          if (current >= target) {
            current = target;
            clearInterval(timer);
          }
          el.textContent = prefix + (isDecimal ? current.toFixed(1) : Math.floor(current).toLocaleString()) + suffix;
        }, stepTime);

        observer.unobserve(el);
      }
    });
  }, { threshold: 0.2 });

  counters.forEach(c => observer.observe(c));
}
