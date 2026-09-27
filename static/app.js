let scenarios = [];
let currentIndex = 0;
let blockedCount = 0;
let trappedCount = 0;
let lastVerificationId = null;

async function loadScenarios() {
  const res = await fetch("/api/scenarios");
  scenarios = await res.json();
  document.getElementById("stat-total").innerText = scenarios.length;
  renderScenario();
}

function renderScenario() {
  if (currentIndex >= scenarios.length) {
    showCompletion();
    return;
  }

  const s = scenarios[currentIndex];
  document.getElementById("scenario-channel").innerText = s.category;
  document.getElementById("scenario-sender").innerText = s.sender;
  document.getElementById("scenario-body").innerText = s.body;
  document.getElementById("inspect-url").innerText = s.fakeUrl;
  document.getElementById("inspect-urgency").innerText = s.urgencyTrigger;
  document.getElementById("inspect-domain").innerText = s.realDomain;
  document.getElementById("scenario-icon").innerText = s.type === "upi" ? "💸" : (s.type === "whatsapp" ? "💬" : "📩");
}

function makeDecision(userMarkedAsScam) {
  const s = scenarios[currentIndex];
  const isCorrect = userMarkedAsScam === s.isScam;

  if (isCorrect) {
    blockedCount++;
    document.getElementById("stat-blocked").innerText = blockedCount;
    showFeedback("✅ Correctly Identified!", "#34D399", s.explanation, s.goldenRule);
  } else {
    trappedCount++;
    document.getElementById("stat-trapped").innerText = trappedCount;
    showFeedback("❌ You Got Trapped!", "#F87171", s.explanation, s.goldenRule);
  }

  updateScorecard();
}

function showFeedback(title, color, explanation, rule) {
  const overlay = document.getElementById("feedback-overlay");
  const titleEl = document.getElementById("feedback-title");
  titleEl.innerText = title;
  titleEl.style.color = color;
  document.getElementById("feedback-explanation").innerText = explanation;
  document.getElementById("feedback-rule").innerText = rule;
  overlay.classList.remove("hidden");
}

function nextScenario() {
  document.getElementById("feedback-overlay").classList.add("hidden");
  currentIndex++;
  document.getElementById("stat-completed").innerText = currentIndex;
  renderScenario();
}

function updateScorecard() {
  const totalAttempted = blockedCount + trappedCount;
  const percent = totalAttempted > 0 ? Math.round((blockedCount / totalAttempted) * 100) : 0;
  document.getElementById("score-percent").innerText = percent + "%";

  if (currentIndex + 1 >= scenarios.length && percent >= 70) {
    document.getElementById("btn-cert").removeAttribute("disabled");
  }
}

function showCompletion() {
  document.getElementById("scenario-bubble").innerHTML = `
    <h3 style="color:#38BDF8; margin-bottom:8px;">🎉 Simulation Completed</h3>
    <p style="font-size:12px; color:#94A3B8;">Aapne saare fraud scenarios test kar liye hain. Apne scorecard ko dekhein aur certificate claim karein.</p>
  `;
  document.querySelector(".phone-actions").style.display = "none";
}

async function claimCertificate() {
  const name = document.getElementById("user-name").value.trim() || "Participant";
  const college = document.getElementById("user-college").value.trim() || "College";
  const percent = document.getElementById("score-percent").innerText.replace("%", "");

  const res = await fetch("/api/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, college, score: parseInt(percent) })
  });
  const data = await res.json();
  lastVerificationId = data.verificationId;

  // Download PDF from Python backend
  window.location.href = `/api/certificate?name=${encodeURIComponent(name)}&college=${encodeURIComponent(college)}&score=${percent}&id=${lastVerificationId}`;
}

loadScenarios();
