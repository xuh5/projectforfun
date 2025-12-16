// API client for project3 web interface

const API = {
    /**
     * Validate a ticker and get company info
     */
    async validateTicker(ticker) {
        const response = await fetch('/api/validate-ticker', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ticker }),
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to validate ticker');
        }
        
        return await response.json();
    },

    /**
     * Generate relationships for a company
     */
    async generateRelationships(sourceCompany, count, includeMetadata = true) {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                source_company: sourceCompany,
                count: count,
                include_metadata: includeMetadata,
            }),
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to generate relationships');
        }
        
        return await response.json();
    },

    /**
     * Submit approved relationships
     */
    async submitApproved(relationships, approvedIndices, sourceCompany) {
        const response = await fetch('/api/approve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                relationships: relationships,
                approved_indices: approvedIndices,
                source_company: sourceCompany,
            }),
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to submit relationships');
        }
        
        return await response.json();
    },

    /**
     * Get existing companies
     */
    async getExistingCompanies() {
        const response = await fetch('/api/existing-companies');
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to get existing companies');
        }
        
        return await response.json();
    },
};

