// Main JavaScript for project3 web interface

// Index page - Generate relationships (one-step process)
if (document.getElementById('generateForm')) {
    const form = document.getElementById('generateForm');
    const validatingStatus = document.getElementById('validatingStatus');
    const generatingStatus = document.getElementById('generatingStatus');
    const error = document.getElementById('error');
    const generateBtn = document.getElementById('generateBtn');
    const tickerInput = document.getElementById('companyTicker');
    
    // One-step process: validate + generate
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const ticker = tickerInput.value.trim().toUpperCase();
        const count = parseInt(document.getElementById('relationshipCount').value);
        const includeMetadata = document.getElementById('includeMetadata')?.checked ?? true;
        
        if (!ticker) {
            showError('Please enter a ticker symbol');
            return;
        }
        
        // Disable form
        generateBtn.disabled = true;
        generateBtn.textContent = 'Processing...';
        hideError();
        
        try {
            // Step 1: Validate ticker
            validatingStatus.classList.remove('hidden');
            const validateData = await API.validateTicker(ticker);
            
            let companyInfo;
            if (validateData.exists) {
                companyInfo = validateData.company;
            } else if (validateData.generated_info) {
                companyInfo = validateData.generated_info;
            } else {
                throw new Error('Failed to get company information');
            }
            
            validatingStatus.classList.add('hidden');
            
            // Step 2: Generate relationships
            generatingStatus.classList.remove('hidden');
            const generateData = await API.generateRelationships(companyInfo, count, includeMetadata);
            
            // Store data and redirect
            sessionStorage.setItem('relationships', JSON.stringify(generateData.relationships));
            sessionStorage.setItem('sourceCompany', JSON.stringify(generateData.source_company));
            window.location.href = '/review';
            
        } catch (err) {
            showError(err.message);
            validatingStatus.classList.add('hidden');
            generatingStatus.classList.add('hidden');
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Relationships';
        }
    });
    
    function showError(message) {
        error.textContent = 'Error: ' + message;
        error.classList.remove('hidden');
    }
    
    function hideError() {
        error.classList.add('hidden');
    }
}

// Review page - Approve relationships
if (document.getElementById('relationshipsList')) {
    let relationships = [];
    let sourceCompany = {};
    const approvedIndices = new Set();
    
    // Load data from sessionStorage
    window.addEventListener('DOMContentLoaded', () => {
        const relationshipsData = sessionStorage.getItem('relationships');
        const sourceCompanyData = sessionStorage.getItem('sourceCompany');
        
        if (!relationshipsData || !sourceCompanyData) {
            window.location.href = '/';
            return;
        }
        
        relationships = JSON.parse(relationshipsData);
        sourceCompany = JSON.parse(sourceCompanyData);
        
        renderPage();
    });
    
    function renderPage() {
        // Render source company info
        const sourceInfo = document.getElementById('sourceInfo');
        sourceInfo.innerHTML = `
            <strong>📍 Source Company:</strong> ${sourceCompany.label} (${sourceCompany.id})
            ${sourceCompany.sector ? ` | <strong>Sector:</strong> ${sourceCompany.sector}` : ''}
        `;
        
        // Update statistics
        updateStatistics();
        
        // Render relationships
        const list = document.getElementById('relationshipsList');
        if (relationships.length === 0) {
            list.innerHTML = '<div class="empty-state">No relationships generated</div>';
            return;
        }
        
        list.innerHTML = relationships.map((rel, index) => {
            const target = rel.target_company;
            const relationship = rel.relationship;
            const metadata = relationship.metadata || {};
            const isApproved = approvedIndices.has(index);
            const cardClass = isApproved ? 'approved' : '';
            
            return `
                <div class="relationship-card ${cardClass}" data-index="${index}">
                    <div class="relationship-header">
                        <span class="relationship-type">${relationship.type.replace('_', ' ')}</span>
                    </div>
                    
                    <div class="target-company">
                        <h3>${target.label} (${target.id})</h3>
                        <p>${target.description}</p>
                        ${target.sector ? `<div style="margin-top:8px"><span class="sector">${target.sector}</span></div>` : ''}
                    </div>
                    
                    <div style="margin-top:15px; padding-top:15px; border-top:1px solid #e0e0e0">
                        <strong style="display:block; margin-bottom:10px">Parameters:</strong>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px">
                            <div>
                                <label style="font-size:12px; color:#666">Strength:</label>
                                <input type="number" step="0.01" min="0" max="1" 
                                       value="${relationship.strength || 0.5}" 
                                       onchange="updateParam(${index}, 'strength', this.value)"
                                       style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px">
                            </div>
                            <div>
                                <label style="font-size:12px; color:#666">Alpha:</label>
                                <input type="number" step="0.01" min="0" max="1" 
                                       value="${metadata.alpha || 0.5}" 
                                       onchange="updateParam(${index}, 'alpha', this.value)"
                                       style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px">
                            </div>
                            <div>
                                <label style="font-size:12px; color:#666">Beta:</label>
                                <input type="number" step="0.01" min="0" max="1" 
                                       value="${metadata.beta || 0.5}" 
                                       onchange="updateParam(${index}, 'beta', this.value)"
                                       style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px">
                            </div>
                            <div>
                                <label style="font-size:12px; color:#666">Decay:</label>
                                <input type="number" step="0.01" min="0" max="1" 
                                       value="${metadata.decay || 0.1}" 
                                       onchange="updateParam(${index}, 'decay', this.value)"
                                       style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px">
                            </div>
                            <div>
                                <label style="font-size:12px; color:#666">Threshold:</label>
                                <input type="number" step="0.01" min="0" max="1" 
                                       value="${metadata.threshold || 0.5}" 
                                       onchange="updateParam(${index}, 'threshold', this.value)"
                                       style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px">
                            </div>
                            <div>
                                <label style="font-size:12px; color:#666">Weight:</label>
                                <input type="number" step="0.01" min="0" max="1" 
                                       value="${metadata.weight || 0.5}" 
                                       onchange="updateParam(${index}, 'weight', this.value)"
                                       style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px">
                            </div>
                        </div>
                    </div>
                    
                    <div class="actions" style="margin-top:15px">
                        <button class="btn btn-approve" onclick="toggleApproval(${index})" ${isApproved ? 'disabled' : ''}>
                            ${isApproved ? '✓ Approved' : 'Approve'}
                        </button>
                        <button class="btn btn-reject" onclick="rejectRelationship(${index})" ${isApproved ? '' : 'disabled'}>
                            Reject
                        </button>
                        <button class="btn" onclick="toggleJson(${index})" 
                                style="background:#607d8b; color:white">
                            Show JSON
                        </button>
                    </div>
                    
                    <div id="json-${index}" style="display:none; margin-top:15px; padding:10px; background:#f5f5f5; border-radius:4px; overflow-x:auto">
                        <pre style="margin:0; font-size:12px; white-space:pre-wrap">${JSON.stringify(rel, null, 2)}</pre>
                    </div>
                </div>
            `;
        }).join('');
        
        // Update submit button
        updateSubmitButton();
    }
    
    function updateStatistics() {
        const total = relationships.length;
        const approved = approvedIndices.size;
        const pending = total - approved;
        
        document.getElementById('totalCount').textContent = total;
        document.getElementById('approvedCount').textContent = approved;
        document.getElementById('pendingCount').textContent = pending;
        
        // Update progress
        const progress = total > 0 ? (approved / total * 100) : 0;
        document.getElementById('progressBar').style.width = `${progress}%`;
        document.getElementById('progressText').textContent = `${approved} of ${total} approved`;
    }
    
    window.updateParam = function(index, param, value) {
        const val = parseFloat(value);
        if (isNaN(val)) return;
        
        if (param === 'strength') {
            relationships[index].relationship.strength = val;
        } else {
            if (!relationships[index].relationship.metadata) {
                relationships[index].relationship.metadata = {};
            }
            relationships[index].relationship.metadata[param] = val;
        }
        
        // Update JSON preview if visible
        const jsonDiv = document.getElementById(`json-${index}`);
        if (jsonDiv && jsonDiv.style.display !== 'none') {
            jsonDiv.querySelector('pre').textContent = JSON.stringify(relationships[index], null, 2);
        }
    };
    
    window.toggleJson = function(index) {
        const jsonDiv = document.getElementById(`json-${index}`);
        const btn = event.target;
        
        if (jsonDiv.style.display === 'none') {
            jsonDiv.style.display = 'block';
            btn.textContent = 'Hide JSON';
            // Update JSON content
            jsonDiv.querySelector('pre').textContent = JSON.stringify(relationships[index], null, 2);
        } else {
            jsonDiv.style.display = 'none';
            btn.textContent = 'Show JSON';
        }
    };
    
    window.toggleApproval = function(index) {
        approvedIndices.add(index);
        renderPage();
    };
    
    window.rejectRelationship = function(index) {
        approvedIndices.delete(index);
        renderPage();
    };
    
    window.approveAll = function() {
        relationships.forEach((_, index) => approvedIndices.add(index));
        renderPage();
    };
    
    window.rejectAll = function() {
        approvedIndices.clear();
        renderPage();
    };
    
    function updateSubmitButton() {
        const submitBtn = document.getElementById('submitBtn');
        const submitBtnText = document.getElementById('submitBtnText');
        const count = approvedIndices.size;
        
        submitBtn.disabled = count === 0;
        
        if (count === 0) {
            submitBtnText.textContent = 'Submit Approved Relationships';
        } else {
            submitBtnText.textContent = `Submit ${count} Approved Relationship${count > 1 ? 's' : ''} to Project1`;
        }
    }
    
    window.submitApproved = async function() {
        if (approvedIndices.size === 0) {
            return;
        }
        
        // Confirmation
        const count = approvedIndices.size;
        if (!confirm(`Are you sure you want to add ${count} relationship${count > 1 ? 's' : ''} to Project1?`)) {
            return;
        }
        
        const submitBtn = document.getElementById('submitBtn');
        const submitBtnText = document.getElementById('submitBtnText');
        const statusMessage = document.getElementById('statusMessage');
        
        submitBtn.disabled = true;
        submitBtnText.textContent = '⏳ Submitting to Project1...';
        statusMessage.style.display = 'none';
        
        try {
            const data = await API.submitApproved(
                relationships,
                Array.from(approvedIndices),
                sourceCompany
            );
            
            const successCount = data.results.filter(r => r.status === 'success').length;
            const errorCount = data.results.filter(r => r.status === 'error').length;
            
            // Show success message
            statusMessage.className = 'status-message success';
            statusMessage.style.display = 'block';
            statusMessage.innerHTML = `
                <strong>✓ Success!</strong><br>
                Successfully added ${successCount} relationship${successCount > 1 ? 's' : ''} to Project1.<br>
                ${errorCount > 0 ? 
                    `<br><strong>⚠️ ${errorCount} Error${errorCount > 1 ? 's' : ''}:</strong><br>${data.results.filter(r => r.status === 'error').map(r => `• ${r.target_company}: ${r.error}`).join('<br>')}` : ''}
                <br><br>Redirecting in 3 seconds...
            `;
            
            // Clear session storage and redirect
            setTimeout(() => {
                sessionStorage.removeItem('relationships');
                sessionStorage.removeItem('sourceCompany');
                window.location.href = '/';
            }, 3000);
            
        } catch (err) {
            statusMessage.className = 'status-message error';
            statusMessage.style.display = 'block';
            statusMessage.innerHTML = `<strong>❌ Error:</strong> ${err.message}`;
            submitBtn.disabled = false;
            submitBtnText.textContent = `Submit ${approvedIndices.size} Approved Relationship${approvedIndices.size > 1 ? 's' : ''} to Project1`;
        }
    };
}

