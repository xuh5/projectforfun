// State
let selectedOptions = [];  // 多选
let currentText = '';
let currentResults = [];   // 多个结果
let options = [];

// 选项缩写映射
const ABBREV = {
  'explain_code': 'Explain',
  'explain_functions': 'Funcs',
  'make_examples': 'Examples',
  'complexity': 'Complex',
  'unit_tests': 'Tests'
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

// Render options (多选，无图标)
function renderOptions() {
  const container = document.getElementById('optionsList');
  container.innerHTML = options.map((opt, index) => {
    const isActive = selectedOptions.includes(opt.key);
    return `
      <button class="option-btn ${isActive ? 'active' : ''}" data-key="${opt.key}" onclick="toggleOption('${opt.key}')">
        <span class="checkbox">${isActive ? '✓' : ''}</span>
        <span class="text">${opt.name}</span>
      </button>
    `;
  }).join('');
}

// Toggle option (多选)
function toggleOption(key) {
  const idx = selectedOptions.indexOf(key);
  if (idx >= 0) {
    selectedOptions.splice(idx, 1);
  } else {
    selectedOptions.push(key);
  }
  
  // Update UI
  renderOptions();
  updateRunButton();
}

// 当前查看的结果索引（-1 表示查看全部）
let currentResultTab = -1;

// 渲染结果切换栏（执行后显示，用于切换查看不同 action 的结果）
function renderResultTabs() {
  const bar = document.getElementById('resultTabsBar');
  const container = document.getElementById('resultTabs');
  
  if (!bar || !container) return;
  
  if (currentResults.length <= 1) {
    bar.style.display = 'none';
    return;
  }
  
  bar.style.display = 'flex';
  
  // 生成按钮：各个 action（无 All）
  const html = currentResults.map((r, idx) => {
    const abbr = ABBREV[r.option] || r.option;
    const isActive = currentResultTab === idx;
    return `<button class="result-tab ${isActive ? 'active' : ''}" onclick="switchResultTab(${idx})">${abbr}</button>`;
  }).join('');
  
  container.innerHTML = html;
}

// 切换查看某个 action 的结果
function switchResultTab(idx) {
  currentResultTab = idx;
  renderResultTabs();
  renderCurrentResults();
}

// 根据当前 tab 渲染结果
function renderCurrentResults() {
  const container = document.getElementById('resultContent');
  
  if (currentResults.length === 0) {
    container.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><div class="empty-text">No results</div></div>';
    return;
  }
  
  // 确保 tab 索引有效
  if (currentResultTab < 0 || currentResultTab >= currentResults.length) {
    currentResultTab = 0;
  }
  
  // 只显示当前选中的那个结果
  const r = currentResults[currentResultTab];
  
  const html = `
    <div class="result-block single">
      <div class="result-block-content">${formatResult(r.content)}</div>
    </div>
  `;
  
  container.innerHTML = html;
}

// Update run button state
function updateRunButton() {
  const btn = document.getElementById('runBtn');
  btn.disabled = selectedOptions.length === 0 || !currentText;
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

// Run action (批量执行多个 action)
async function runAction() {
  if (selectedOptions.length === 0 || !currentText) return;
  
  showLoading(true);
  
  try {
    // 批量处理所有选中的 actions
    const result = await pywebview.api.process_batch(currentText, selectedOptions);
    displayBatchResult(result);
    await loadHistory();
  } catch (e) {
    displayError(e.message || 'An error occurred');
  }
  
  showLoading(false);
}

// Display batch result (多个 action 的结果)
function displayBatchResult(batchResult) {
  const status = document.getElementById('resultStatus');
  const copyBtn = document.getElementById('copyBtn');
  
  currentResults = batchResult.results || [];
  currentResultTab = 0;  // 默认显示第一个
  
  // 渲染切换栏和结果
  renderResultTabs();
  renderCurrentResults();
  
  if (currentResults.length === 0) return;
  
  // Update overall status
  const allValid = currentResults.every(r => r.valid);
  const someValid = currentResults.some(r => r.valid);
  status.className = 'status ' + (allValid ? 'success' : someValid ? 'partial' : 'error');
  status.textContent = allValid ? '✓ All Valid' : someValid ? '⚠ Partial' : '✗ All Failed';
  
  // Show copy button
  copyBtn.style.display = currentResults.length > 0 ? 'flex' : 'none';
}

// Display single result (兼容历史记录回显)
function displayResult(result) {
  displayBatchResult({ results: [result] });
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

// Render history (新格式：一条记录可有多个 action)
function renderHistory(records) {
  const container = document.getElementById('historyList');
  const countEl = document.getElementById('historyCount');
  const clearBtn = document.getElementById('clearAllBtn');
  
  countEl.textContent = `${records.length} / 10`;
  clearBtn.style.display = records.length > 0 ? 'flex' : 'none';
  
  if (records.length === 0) {
    container.innerHTML = '<div class="empty-history">No history yet</div>';
    return;
  }
  
  container.innerHTML = records.map(r => {
    // 解析 actions（可能是数组或单个字符串）
    const actions = Array.isArray(r.options) ? r.options : [r.option];
    const actionTags = actions.map(a => {
      const abbr = ABBREV[a] || a;
      return `<span class="history-tag">${escapeHtml(abbr)}</span>`;
    }).join('');
    
    // 计算整体状态
    const allValid = r.all_valid !== undefined ? r.all_valid : r.valid;
    
    return `
      <div class="history-item">
        <div class="history-item-content" onclick="loadRecord(${r.id})">
          <div class="status-dot ${allValid ? 'success' : 'error'}"></div>
          <div class="info">
            <div class="history-tags">${actionTags}</div>
            <div class="preview">${escapeHtml(r.input_text.substring(0, 30))}...</div>
            <div class="time">${r.timestamp}</div>
          </div>
        </div>
        <div class="delete-panel" onclick="deleteRecord(event, ${r.id})">
          <span>🗑️</span>
        </div>
      </div>
    `;
  }).join('');
}

// Delete single record
async function deleteRecord(event, id) {
  event.stopPropagation(); // Prevent loading the record
  
  try {
    await pywebview.api.delete_record(id);
    await loadHistory();
  } catch (e) {
    console.error('Failed to delete record:', e);
  }
}

// Clear all history
async function clearAllHistory() {
  if (!confirm('Are you sure you want to delete all history?')) return;
  
  try {
    await pywebview.api.clear_history();
    await loadHistory();
  } catch (e) {
    console.error('Failed to clear history:', e);
  }
}

// Load record into view (支持多个 action 的记录)
async function loadRecord(id) {
  try {
    const record = await pywebview.api.get_record(id);
    if (record) {
      setInputText(record.input_text);
      
      // 如果有 results 数组（新格式），使用批量显示
      if (record.results && Array.isArray(record.results) && record.results.length > 0) {
        displayBatchResult({ results: record.results });
      } else if (record.result) {
        // 兼容旧格式
        displayBatchResult({ 
          results: [{ 
            option: record.option, 
            content: record.result, 
            valid: record.valid 
          }] 
        });
      }
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

function switchSettingsTab(tabName) {
  // Update nav items
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.tab === tabName);
  });
  
  // Update tab content
  document.querySelectorAll('.settings-tab').forEach(tab => {
    tab.classList.toggle('active', tab.id === `tab-${tabName}`);
  });
}

function toggleApiKeyVisibility() {
  const input = document.getElementById('apiKey');
  input.type = input.type === 'password' ? 'text' : 'password';
}

async function loadSettings() {
  try {
    // 先加载模型列表
    await loadModels();
    
    // 再加载设置
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

// 加载模型列表
async function loadModels() {
  try {
    const groups = await pywebview.api.get_models();
    const select = document.getElementById('model');
    
    select.innerHTML = groups.map(g => `
      <optgroup label="${g.group}">
        ${g.models.map(m => `<option value="${m.value}">${m.name}</option>`).join('')}
      </optgroup>
    `).join('');
  } catch (e) {
    console.error('Failed to load models:', e);
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

// Copy result to clipboard (复制当前选中的结果)
function copyResult() {
  if (!currentResults || currentResults.length === 0) return;
  
  // 复制当前选中的结果
  const r = currentResults[currentResultTab] || currentResults[0];
  const content = r.content || '';
  
  navigator.clipboard.writeText(content).then(() => {
    const btn = document.getElementById('copyBtn');
    btn.classList.add('copied');
    btn.querySelector('.copy-text').textContent = 'Copied!';
    
    setTimeout(() => {
      btn.classList.remove('copied');
      btn.querySelector('.copy-text').textContent = 'Copy';
    }, 1500);
  }).catch(err => {
    console.error('Failed to copy:', err);
  });
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
