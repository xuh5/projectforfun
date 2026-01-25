// State
let selectedOption = null;
let currentText = '';
let options = [];

// Icons for options
const ICONS = {
  'explain_code': '📖',
  'explain_functions': '🔍',
  'make_examples': '💡',
  'complexity': '⏱️',
  'unit_tests': '🧪'
};

// Initialize - wait for pywebview to be ready
async function init() {
  console.log('[App] Initializing...');
  await loadOptions();
  await loadHistory();
  await loadSettings();
  console.log('[App] Initialized successfully');
  
  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.ctrlKey) {
      runAction();
    }
    if (e.key === 'Escape') {
      const modal = document.getElementById('settingsModal');
      if (modal.classList.contains('show')) {
        toggleSettings();
      }
    }
  });
}

// Wait for pywebview API to be ready
if (window.pywebview) {
  init();
} else {
  window.addEventListener('pywebviewready', init);
}

// Load options from backend
async function loadOptions() {
  try {
    const result = await pywebview.api.get_options();
    options = result;
    renderOptions();
  } catch (e) {
    console.error('Failed to load options:', e);
  }
}

// Render options
function renderOptions() {
  const container = document.getElementById('optionsList');
  container.innerHTML = options.map((opt, index) => `
    <button class="option-btn" data-key="${opt.key}" onclick="selectOption('${opt.key}')">
      <span class="icon">${ICONS[opt.key] || '📌'}</span>
      <span class="text">${opt.name}</span>
    </button>
  `).join('');
}

// Select option
function selectOption(key) {
  selectedOption = key;
  
  // Update UI
  document.querySelectorAll('.option-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.key === key);
  });
  
  updateRunButton();
}

// Update run button state
function updateRunButton() {
  const btn = document.getElementById('runBtn');
  btn.disabled = !selectedOption || !currentText;
}

// Set input text (called from Python)
function setInputText(text) {
  currentText = text;
  const container = document.getElementById('inputText');
  
  if (text) {
    container.innerHTML = `<code>${escapeHtml(text)}</code>`;
  } else {
    container.innerHTML = '<span class="placeholder">Press Ctrl+Q to capture selected text...</span>';
  }
  
  updateRunButton();
}

// Run action
async function runAction() {
  if (!selectedOption || !currentText) return;
  
  showLoading(true);
  
  try {
    const result = await pywebview.api.process_text(currentText, selectedOption);
    displayResult(result);
    await loadHistory();
  } catch (e) {
    displayError(e.message || 'An error occurred');
  }
  
  showLoading(false);
}

// Display result
function displayResult(result) {
  const container = document.getElementById('resultContent');
  const status = document.getElementById('resultStatus');
  
  // Format result (simple markdown-like rendering)
  let html = formatResult(result.content);
  container.innerHTML = html;
  
  // Update status
  status.className = 'status ' + (result.valid ? 'success' : 'error');
  status.textContent = result.valid ? '✓ Valid Response' : '✗ Invalid Format';
}

// Display error
function displayError(message) {
  const container = document.getElementById('resultContent');
  const status = document.getElementById('resultStatus');
  
  container.innerHTML = `<div class="error-message">❌ ${escapeHtml(message)}</div>`;
  status.className = 'status error';
  status.textContent = '✗ Error';
}

// Format result content
function formatResult(text) {
  if (!text) return '';
  
  // Escape HTML first
  let html = escapeHtml(text);
  
  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
  
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  
  // Headers
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^# (.+)$/gm, '<h3>$1</h3>');
  
  // Line breaks
  html = html.replace(/\n/g, '<br>');
  
  return html;
}

// Load history
async function loadHistory() {
  try {
    const records = await pywebview.api.get_history();
    renderHistory(records);
  } catch (e) {
    console.error('Failed to load history:', e);
  }
}

// Render history
function renderHistory(records) {
  const container = document.getElementById('historyList');
  const countEl = document.getElementById('historyCount');
  
  countEl.textContent = `${records.length} / 10`;
  
  if (records.length === 0) {
    container.innerHTML = '<div class="empty-history">No history yet</div>';
    return;
  }
  
  container.innerHTML = records.map(r => `
    <div class="history-item" onclick="loadRecord(${r.id})">
      <div class="status-dot ${r.valid ? 'success' : 'error'}"></div>
      <div class="info">
        <div class="option-name">${escapeHtml(r.option)}</div>
        <div class="preview">${escapeHtml(r.input_text.substring(0, 30))}...</div>
        <div class="time">${r.timestamp}</div>
      </div>
    </div>
  `).join('');
}

// Load record into view
async function loadRecord(id) {
  try {
    const record = await pywebview.api.get_record(id);
    if (record) {
      setInputText(record.input_text);
      displayResult({ content: record.result, valid: record.valid });
    }
  } catch (e) {
    console.error('Failed to load record:', e);
  }
}

// Settings
function toggleSettings() {
  const modal = document.getElementById('settingsModal');
  modal.classList.toggle('show');
}

function toggleApiKeyVisibility() {
  const input = document.getElementById('apiKey');
  input.type = input.type === 'password' ? 'text' : 'password';
}

async function loadSettings() {
  try {
    const settings = await pywebview.api.get_settings();
    document.getElementById('apiUrl').value = settings.api_url || '';
    document.getElementById('apiKey').value = settings.api_key || '';
    document.getElementById('model').value = settings.model || 'gpt-3.5-turbo';
    document.getElementById('timeout').value = settings.timeout || 30;
    document.getElementById('mockMode').checked = settings.mock_mode !== false;
    updateModeIndicator(settings.mock_mode !== false);
  } catch (e) {
    console.error('Failed to load settings:', e);
  }
}

async function saveSettings() {
  const mockMode = document.getElementById('mockMode').checked;
  const settings = {
    api_url: document.getElementById('apiUrl').value,
    api_key: document.getElementById('apiKey').value,
    model: document.getElementById('model').value,
    timeout: parseInt(document.getElementById('timeout').value) || 30,
    mock_mode: mockMode
  };
  
  try {
    await pywebview.api.save_settings(settings);
    toggleSettings();
    updateModeIndicator(mockMode);
    showToast('Settings saved!');
  } catch (e) {
    console.error('Failed to save settings:', e);
    showToast('Failed to save settings', true);
  }
}

function updateModeIndicator(isMock) {
  // Update title to show current mode
  const title = document.querySelector('.title');
  let badge = title.querySelector('.mode-badge');
  if (!badge) {
    badge = document.createElement('span');
    badge.className = 'mode-badge';
    title.appendChild(badge);
  }
  badge.textContent = isMock ? 'Mock' : 'Live';
  badge.className = 'mode-badge ' + (isMock ? 'mock' : 'live');
}

// Loading
function showLoading(show) {
  document.getElementById('loadingOverlay').classList.toggle('show', show);
}

// Toast notification (simple)
function showToast(message, isError = false) {
  // Simple alert for now, can be improved later
  console.log(message);
}

// Utility
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Expose to Python
window.setInputText = setInputText;
window.refreshHistory = loadHistory;
