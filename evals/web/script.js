document.addEventListener('DOMContentLoaded', () => {
  const data = window.EVAL_DATA || [];

  // State
  let currentFilter = {
    scenario: 'all',
    result: 'all'
  };
  let selectedRunId = null;

  // DOM Elements
  const runListEl = document.getElementById('run-list');
  const detailViewEl = document.getElementById('detail-view');
  const scenarioFilterEl = document.getElementById('scenario-filter');
  const resultFilterEl = document.getElementById('result-filter');
  const headerStatsEl = document.getElementById('header-stats');

  // Initialize
  init();

  function init() {
    populateFilters();
    renderStats();
    renderRunList();

    // Event Listeners
    scenarioFilterEl.addEventListener('change', (e) => {
      currentFilter.scenario = e.target.value;
      renderRunList();
    });

    resultFilterEl.addEventListener('change', (e) => {
      currentFilter.result = e.target.value;
      renderRunList();
    });
  }

  function populateFilters() {
    const scenarios = new Set(data.map(r => r.scenario).filter(Boolean));
    [...scenarios].sort().forEach(s => {
      const option = document.createElement('option');
      option.value = s;
      option.textContent = s;
      scenarioFilterEl.appendChild(option);
    });
  }

  function renderStats() {
    const totalRuns = data.length;
    const passCount = data.filter(r => r._is_pass).length;
    const passRate = totalRuns > 0 ? Math.round((passCount / totalRuns) * 100) : 0;

    // Calculate average score
    const scores = data.map(r => r._total_score).filter(s => s > 0);
    const avgScore = scores.length > 0
      ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
      : '-';

    headerStatsEl.innerHTML = `
            <div class="stat-item"><strong>${totalRuns}</strong> Runs</div>
            <div class="stat-item"><strong>${passRate}%</strong> Pass Rate</div>
            <div class="stat-item"><strong>${avgScore}</strong> Avg Score</div>
        `;
  }

  function renderRunList() {
    runListEl.innerHTML = '';

    const filteredData = data.filter(r => {
      const matchScenario = currentFilter.scenario === 'all' || r.scenario === currentFilter.scenario;
      const matchResult = currentFilter.result === 'all' ||
        (currentFilter.result === 'pass' && r._is_pass) ||
        (currentFilter.result === 'fail' && !r._is_pass);
      return matchScenario && matchResult;
    });

    filteredData.forEach((run, index) => {
      // Use index as a temporary ID reference if needed, but better to compare objects
      const el = document.createElement('div');
      el.className = `run-item ${selectedRunId === run ? 'active' : ''}`;
      el.onclick = () => selectRun(run, el);

      const statusClass = run._is_pass ? 'status-pass' : 'status-fail';
      const statusText = run._is_pass ? 'PASS' : 'FAIL';
      const score = run._total_score > 0 ? run._total_score : '-';
      const runId = run.run_config?.run_id || '?';
      const timestamp = formatTimestamp(run.timestamp);

      el.innerHTML = `
                <div class="run-header">
                    <span class="scenario-name">${run.scenario || 'Unknown'}</span>
                    <span class="run-score">${score}</span>
                </div>
                <div class="run-meta">
                    <span>Run #${runId} • ${timestamp}</span>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
            `;
      runListEl.appendChild(el);
    });
  }

  function selectRun(run, el) {
    // Update active class
    document.querySelectorAll('.run-item').forEach(i => i.classList.remove('active'));
    el.classList.add('active');
    selectedRunId = run;

    renderDetailView(run);
  }

  function renderDetailView(run) {
    const isPass = run._is_pass;
    const score = run._total_score > 0 ? run._total_score : '-';
    const statusColor = isPass ? 'var(--success-color)' : 'var(--danger-color)';
    const statusText = isPass ? 'PASS' : 'FAIL';

    let content = `
            <div class="detail-container">
                <div class="detail-header">
                    <div class="detail-title">
                        <h2>${run.scenario}</h2>
                        <div class="run-id">
                            Run ID: ${run.run_config?.run_id || '-'} • 
                            Timestamp: ${run.timestamp} • 
                            <span style="color: ${statusColor}; font-weight: 700">${statusText}</span>
                        </div>
                    </div>
                    <div class="detail-score">
                        <div class="big-score">${score}</div>
                        <div class="score-label">Total Score</div>
                    </div>
                </div>
        `;

    // Rubric Section
    const rubricGrade = run.grades?.find(g => g.metric === 'rubric_eval');
    if (rubricGrade && rubricGrade.scores) {
      content += `<div class="section-title">Rubric Evaluation</div>`;
      content += `<table class="rubric-table">
                <thead>
                    <tr>
                        <th>Dimension</th>
                        <th>Score</th>
                        <th>Reasoning</th>
                    </tr>
                </thead>
                <tbody>`;

      for (const [dim, val] of Object.entries(rubricGrade.scores)) {
        const reasoning = rubricGrade.reasoning?.[dim] || '-';
        content += `
                    <tr>
                        <td class="dim-name">${dim}</td>
                        <td class="dim-score">${val}</td>
                        <td class="dim-reason">${reasoning}</td>
                    </tr>
                `;
      }
      content += `</tbody></table>`;
    }

    // Transcript Section
    if (run.transcript && run.transcript.length > 0) {
      content += `<div class="section-title">Transcript</div>`;
      content += `<div class="transcript-container">`;

      run.transcript.forEach(line => {
        const isPlayer = line.speaker.toLowerCase() === 'player' || line.speaker.toLowerCase() === 'user';
        const roleClass = isPlayer ? 'role-player' : 'role-npc';

        content += `
                    <div class="chat-bubble ${roleClass}">
                        <div class="speaker-label">${line.speaker}</div>
                        <div class="bubble-content">${escapeHtml(line.content)}</div>
                    </div>
                `;
      });

      content += `</div>`;
    }

    content += `</div>`; // Close detail-container
    detailViewEl.innerHTML = content;
  }

  function formatTimestamp(ts) {
    if (!ts) return '';
    // Expecting format like 20260122_181745
    if (ts.length === 15 && ts.includes('_')) {
      const datePart = ts.split('_')[0];
      const timePart = ts.split('_')[1];
      return `${datePart.slice(4, 6)}/${datePart.slice(6, 8)} ${timePart.slice(0, 2)}:${timePart.slice(2, 4)}`;
    }
    return ts;
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
