// Global state
let currentPromptId = null;
let currentTab = 'generate';

// API Base URL
const API_BASE = '/api/prompts';

// DOM Elements
const elements = {
    // Navigation
    navBtns: document.querySelectorAll('.nav-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // Generate tab
    userInput: document.getElementById('user-input'),
    aiTool: document.getElementById('ai-tool'),
    outputStyle: document.getElementById('output-style'),
    category: document.getElementById('category'),
    seoKeywords: document.getElementById('seo-keywords'),
    generateBtn: document.getElementById('generate-btn'),
    
    // Improve tab
    existingPrompt: document.getElementById('existing-prompt'),
    improveAiTool: document.getElementById('improve-ai-tool'),
    improveOutputStyle: document.getElementById('improve-output-style'),
    improveCategory: document.getElementById('improve-category'),
    improveBtn: document.getElementById('improve-btn'),
    
    // Analyze tab
    analyzePrompt: document.getElementById('analyze-prompt'),
    analyzeAiTool: document.getElementById('analyze-ai-tool'),
    analyzeCategory: document.getElementById('analyze-category'),
    analyzeBtn: document.getElementById('analyze-btn'),
    
    // Results
    resultsSection: document.getElementById('results-section'),
    generatedPrompt: document.getElementById('generated-prompt'),
    analysisContent: document.getElementById('analysis-content'),
    scoreValue: document.getElementById('score-value'),
    scoreLabel: document.getElementById('score-label'),
    
    // Actions
    copyBtn: document.getElementById('copy-btn'),
    exportTxtBtn: document.getElementById('export-txt-btn'),
    exportJsonBtn: document.getElementById('export-json-btn'),
    
    // History
    historyContent: document.getElementById('history-content'),
    
    // Loading
    loadingOverlay: document.getElementById('loading-overlay'),
    toastContainer: document.getElementById('toast-container')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        // Load dropdown options
        await loadDropdownOptions();
        
        // Set up event listeners
        setupEventListeners();
        
        // Load history if on history tab
        if (currentTab === 'history') {
            await loadHistory();
        }
        
        showToast('Application loaded successfully!', 'success');
    } catch (error) {
        console.error('Failed to initialize app:', error);
        showToast('Failed to load application. Please refresh the page.', 'error');
    }
}

async function loadDropdownOptions() {
    try {
        // Load AI tools
        const aiToolsResponse = await fetch(`${API_BASE}/ai-tools`);
        const aiToolsData = await aiToolsResponse.json();
        
        if (aiToolsData.success) {
            populateSelect(elements.aiTool, aiToolsData.data);
            populateSelect(elements.improveAiTool, aiToolsData.data);
            populateSelect(elements.analyzeAiTool, aiToolsData.data);
        }
        
        // Load output styles
        const stylesResponse = await fetch(`${API_BASE}/output-styles`);
        const stylesData = await stylesResponse.json();
        
        if (stylesData.success) {
            populateSelect(elements.outputStyle, stylesData.data);
            populateSelect(elements.improveOutputStyle, stylesData.data);
        }
        
        // Load categories
        const categoriesResponse = await fetch(`${API_BASE}/categories`);
        const categoriesData = await categoriesResponse.json();
        
        if (categoriesData.success) {
            populateSelect(elements.category, categoriesData.data);
            populateSelect(elements.improveCategory, categoriesData.data);
            populateSelect(elements.analyzeCategory, categoriesData.data);
        }
        
    } catch (error) {
        console.error('Failed to load dropdown options:', error);
        throw error;
    }
}

function populateSelect(selectElement, options) {
    // Clear existing options except the first one
    while (selectElement.children.length > 1) {
        selectElement.removeChild(selectElement.lastChild);
    }
    
    // Add new options
    Object.entries(options).forEach(([value, label]) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = label;
        selectElement.appendChild(option);
    });
}

function setupEventListeners() {
    // Navigation
    elements.navBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // Generate button
    elements.generateBtn.addEventListener('click', handleGenerate);
    
    // Improve button
    elements.improveBtn.addEventListener('click', handleImprove);
    
    // Analyze button
    elements.analyzeBtn.addEventListener('click', handleAnalyze);
    
    // Action buttons
    elements.copyBtn.addEventListener('click', copyPrompt);
    elements.exportTxtBtn.addEventListener('click', () => exportPrompt('txt'));
    elements.exportJsonBtn.addEventListener('click', () => exportPrompt('json'));
    
    // Enter key handling for textareas
    [elements.userInput, elements.existingPrompt, elements.analyzePrompt].forEach(textarea => {
        textarea.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                const tab = textarea.closest('.tab-content').id.replace('-tab', '');
                if (tab === 'generate') handleGenerate();
                else if (tab === 'improve') handleImprove();
                else if (tab === 'analyze') handleAnalyze();
            }
        });
    });
}

function switchTab(tabName) {
    currentTab = tabName;
    
    // Update navigation
    elements.navBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update tab content
    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
    
    // Load history if switching to history tab
    if (tabName === 'history') {
        loadHistory();
    }
    
    // Hide results when switching tabs
    elements.resultsSection.style.display = 'none';
}

async function handleGenerate() {
    const data = {
        user_input: elements.userInput.value.trim(),
        ai_tool: elements.aiTool.value,
        output_style: elements.outputStyle.value,
        category: elements.category.value,
        seo_keywords: elements.seoKeywords.value.trim()
    };
    
    if (!validateGenerateForm(data)) return;
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentPromptId = result.data.id;
            displayResults(result.data);
            showToast('Prompt generated successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to generate prompt');
        }
        
    } catch (error) {
        console.error('Generate error:', error);
        showToast('Failed to generate prompt. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleImprove() {
    const data = {
        existing_prompt: elements.existingPrompt.value.trim(),
        ai_tool: elements.improveAiTool.value,
        output_style: elements.improveOutputStyle.value,
        category: elements.improveCategory.value
    };
    
    if (!validateImproveForm(data)) return;
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/improve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentPromptId = result.data.id;
            displayResults(result.data);
            showToast('Prompt improved successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to improve prompt');
        }
        
    } catch (error) {
        console.error('Improve error:', error);
        showToast('Failed to improve prompt. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleAnalyze() {
    const data = {
        prompt: elements.analyzePrompt.value.trim(),
        ai_tool: elements.analyzeAiTool.value,
        category: elements.analyzeCategory.value
    };
    
    if (!validateAnalyzeForm(data)) return;
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayAnalysisResults(result.data);
            showToast('Prompt analyzed successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to analyze prompt');
        }
        
    } catch (error) {
        console.error('Analyze error:', error);
        showToast('Failed to analyze prompt. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function validateGenerateForm(data) {
    if (!data.user_input) {
        showToast('Please describe what you want to create.', 'error');
        elements.userInput.focus();
        return false;
    }
    
    if (!data.ai_tool) {
        showToast('Please select an AI tool.', 'error');
        elements.aiTool.focus();
        return false;
    }
    
    if (!data.output_style) {
        showToast('Please select an output style.', 'error');
        elements.outputStyle.focus();
        return false;
    }
    
    if (!data.category) {
        showToast('Please select a category.', 'error');
        elements.category.focus();
        return false;
    }
    
    return true;
}

function validateImproveForm(data) {
    if (!data.existing_prompt) {
        showToast('Please enter your existing prompt.', 'error');
        elements.existingPrompt.focus();
        return false;
    }
    
    if (!data.ai_tool) {
        showToast('Please select an AI tool.', 'error');
        elements.improveAiTool.focus();
        return false;
    }
    
    if (!data.output_style) {
        showToast('Please select an output style.', 'error');
        elements.improveOutputStyle.focus();
        return false;
    }
    
    if (!data.category) {
        showToast('Please select a category.', 'error');
        elements.improveCategory.focus();
        return false;
    }
    
    return true;
}

function validateAnalyzeForm(data) {
    if (!data.prompt) {
        showToast('Please enter a prompt to analyze.', 'error');
        elements.analyzePrompt.focus();
        return false;
    }
    
    if (!data.ai_tool) {
        showToast('Please select an AI tool.', 'error');
        elements.analyzeAiTool.focus();
        return false;
    }
    
    if (!data.category) {
        showToast('Please select a category.', 'error');
        elements.analyzeCategory.focus();
        return false;
    }
    
    return true;
}

function displayResults(data) {
    elements.generatedPrompt.querySelector('code').textContent = data.generated_prompt;
    elements.analysisContent.textContent = data.analysis;
    
    // Animate score
    animateScore(data.score);
    
    // Show results section
    elements.resultsSection.style.display = 'block';
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayAnalysisResults(data) {
    elements.generatedPrompt.querySelector('code').textContent = elements.analyzePrompt.value;
    elements.analysisContent.textContent = data.analysis;
    
    // Animate score
    animateScore(data.score);
    
    // Show results section
    elements.resultsSection.style.display = 'block';
    elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function animateScore(targetScore) {
    const scoreElement = elements.scoreValue;
    const labelElement = elements.scoreLabel;
    
    let currentScore = 0;
    const increment = targetScore / 50; // 50 steps for smooth animation
    
    const animation = setInterval(() => {
        currentScore += increment;
        
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(animation);
        }
        
        scoreElement.textContent = Math.round(currentScore);
        
        // Update label based on score
        if (currentScore >= 90) {
            labelElement.textContent = 'Excellent';
            labelElement.style.color = '#28a745';
        } else if (currentScore >= 80) {
            labelElement.textContent = 'Very Good';
            labelElement.style.color = '#17a2b8';
        } else if (currentScore >= 70) {
            labelElement.textContent = 'Good';
            labelElement.style.color = '#ffc107';
        } else if (currentScore >= 60) {
            labelElement.textContent = 'Fair';
            labelElement.style.color = '#fd7e14';
        } else {
            labelElement.textContent = 'Needs Improvement';
            labelElement.style.color = '#dc3545';
        }
    }, 20);
}

async function copyPrompt() {
    try {
        const promptText = elements.generatedPrompt.querySelector('code').textContent;
        await navigator.clipboard.writeText(promptText);
        showToast('Prompt copied to clipboard!', 'success');
    } catch (error) {
        console.error('Copy error:', error);
        showToast('Failed to copy prompt. Please select and copy manually.', 'error');
    }
}

async function exportPrompt(format) {
    if (!currentPromptId) {
        showToast('No prompt to export.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/export/${currentPromptId}?format=${format}`);
        
        if (format === 'txt') {
            const text = await response.text();
            downloadFile(text, `prompt_${currentPromptId}.txt`, 'text/plain');
        } else {
            const data = await response.json();
            const jsonString = JSON.stringify(data, null, 2);
            downloadFile(jsonString, `prompt_${currentPromptId}.json`, 'application/json');
        }
        
        showToast(`Prompt exported as ${format.toUpperCase()}!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showToast('Failed to export prompt.', 'error');
    }
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/history?per_page=20`);
        const result = await response.json();
        
        if (result.success) {
            displayHistory(result.data.prompts);
        } else {
            throw new Error(result.error || 'Failed to load history');
        }
    } catch (error) {
        console.error('History error:', error);
        elements.historyContent.innerHTML = '<p>Failed to load history. Please try again.</p>';
    }
}

function displayHistory(prompts) {
    if (prompts.length === 0) {
        elements.historyContent.innerHTML = `
            <div class="text-center" style="padding: 3rem; color: #666;">
                <i class="fas fa-history" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                <p>No prompts generated yet. Start by creating your first prompt!</p>
            </div>
        `;
        return;
    }
    
    elements.historyContent.innerHTML = prompts.map(prompt => `
        <div class="history-item" onclick="loadHistoryItem(${prompt.id})">
            <div class="history-item-header">
                <div class="history-item-meta">
                    <span><i class="fas fa-robot"></i> ${prompt.ai_tool}</span>
                    <span><i class="fas fa-tag"></i> ${prompt.category}</span>
                    <span><i class="fas fa-star"></i> ${prompt.score}/100</span>
                </div>
                <span style="font-size: 0.8rem; color: #999;">
                    ${new Date(prompt.created_at).toLocaleDateString()}
                </span>
            </div>
            <div class="history-item-preview">
                ${prompt.original_input.substring(0, 150)}${prompt.original_input.length > 150 ? '...' : ''}
            </div>
        </div>
    `).join('');
}

async function loadHistoryItem(promptId) {
    try {
        const response = await fetch(`${API_BASE}/export/${promptId}?format=json`);
        const result = await response.json();
        
        if (result.success) {
            currentPromptId = promptId;
            displayResults(result.data);
            showToast('Historical prompt loaded!', 'success');
        } else {
            throw new Error(result.error || 'Failed to load prompt');
        }
    } catch (error) {
        console.error('Load history item error:', error);
        showToast('Failed to load prompt.', 'error');
    }
}

function showLoading(show) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
    
    // Remove on click
    toast.addEventListener('click', () => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + 1-4 for tab switching
    if ((e.ctrlKey || e.metaKey) && e.key >= '1' && e.key <= '4') {
        e.preventDefault();
        const tabs = ['generate', 'improve', 'analyze', 'history'];
        switchTab(tabs[parseInt(e.key) - 1]);
    }
    
    // Escape to hide results
    if (e.key === 'Escape' && elements.resultsSection.style.display !== 'none') {
        elements.resultsSection.style.display = 'none';
    }
});

