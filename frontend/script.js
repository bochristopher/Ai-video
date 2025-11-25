// API Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const videoForm = document.getElementById('videoForm');
const generateBtn = document.getElementById('generateBtn');
const statusSection = document.getElementById('statusSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const jobsList = document.getElementById('jobsList');

// State
let currentJobId = null;
let statusCheckInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Video Generator initialized');
    setupEventListeners();
    loadRecentJobs();
    fetchAvailableModels();
});

// Event Listeners
function setupEventListeners() {
    console.log('Setting up event listeners');

    videoForm.addEventListener('submit', handleFormSubmit);

    // Example prompt chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.getAttribute('data-prompt');
            document.getElementById('prompt').value = prompt;
            console.log('Example prompt selected:', prompt);
        });
    });

    // Generate another video button
    document.getElementById('generateAnotherBtn')?.addEventListener('click', () => {
        console.log('Generate another video clicked');
        resetForm();
    });

    // Retry button
    document.getElementById('retryBtn')?.addEventListener('click', () => {
        console.log('Retry clicked');
        resetForm();
    });
}

// Form Submission
async function handleFormSubmit(e) {
    e.preventDefault();
    console.log('Form submitted');

    const formData = new FormData(videoForm);
    const data = {
        prompt: formData.get('prompt'),
        model: formData.get('model'),
        duration: parseInt(formData.get('duration')),
    };

    console.log('Generating video with parameters:', data);

    // Disable form and show loading
    setButtonLoading(true);
    hideAllSections();

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        console.log('Generation response:', result);

        if (!response.ok) {
            throw new Error(result.error || 'Failed to start video generation');
        }

        currentJobId = result.job_id;
        console.log('Job started with ID:', currentJobId);

        // Show status section and start polling
        showStatus(currentJobId, data.prompt);
        startStatusPolling();

    } catch (error) {
        console.error('Error generating video:', error);
        showError(error.message);
        setButtonLoading(false);
    }
}

// Status Polling
function startStatusPolling() {
    console.log('Starting status polling for job:', currentJobId);

    // Clear any existing interval
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }

    // Poll every 2 seconds
    statusCheckInterval = setInterval(() => {
        checkJobStatus(currentJobId);
    }, 2000);

    // Check immediately
    checkJobStatus(currentJobId);
}

async function checkJobStatus(jobId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
        const job = await response.json();

        console.log('Job status update:', job);

        if (!response.ok) {
            throw new Error(job.error || 'Failed to check status');
        }

        // Update status display
        updateStatusDisplay(job);

        // Handle completion
        if (job.status === 'completed') {
            console.log('Video generation completed!');
            clearInterval(statusCheckInterval);
            showResults(job);
            setButtonLoading(false);
            loadRecentJobs();
        }

        // Handle failure
        if (job.status === 'failed') {
            console.error('Video generation failed:', job.error);
            clearInterval(statusCheckInterval);
            showError(job.error || 'Video generation failed');
            setButtonLoading(false);
        }

    } catch (error) {
        console.error('Error checking status:', error);
        clearInterval(statusCheckInterval);
        showError('Failed to check generation status');
        setButtonLoading(false);
    }
}

// UI Updates
function updateStatusDisplay(job) {
    document.getElementById('jobId').textContent = job.id;
    document.getElementById('statusPrompt').textContent = job.prompt;

    const statusBadge = document.getElementById('status');
    statusBadge.textContent = job.status.toUpperCase();
    statusBadge.className = `status-badge ${job.status}`;

    const progress = job.progress || 0;
    document.getElementById('progressBar').style.width = `${progress}%`;
    document.getElementById('progressPercent').textContent = progress;

    console.log(`Progress: ${progress}% - Status: ${job.status}`);
}

function showStatus(jobId, prompt) {
    console.log('Showing status section');
    hideAllSections();
    statusSection.style.display = 'block';

    document.getElementById('jobId').textContent = jobId;
    document.getElementById('statusPrompt').textContent = prompt;
    document.getElementById('status').textContent = 'QUEUED';
    document.getElementById('status').className = 'status-badge queued';
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('progressPercent').textContent = '0';
}

function showResults(job) {
    console.log('Showing results section');
    hideAllSections();
    resultsSection.style.display = 'block';

    const videoSource = document.getElementById('videoSource');
    const videoPlayer = document.getElementById('videoPlayer');
    const downloadBtn = document.getElementById('downloadBtn');

    videoSource.src = job.video_url;
    videoPlayer.load();

    downloadBtn.href = job.video_url;
    downloadBtn.download = `ai_video_${job.id}.mp4`;

    console.log('Video ready at:', job.video_url);
}

function showError(message) {
    console.error('Showing error:', message);
    hideAllSections();
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

function hideAllSections() {
    statusSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

function resetForm() {
    console.log('Resetting form');
    hideAllSections();
    setButtonLoading(false);
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    currentJobId = null;
}

function setButtonLoading(loading) {
    const btnText = generateBtn.querySelector('.btn-text');
    const btnLoader = generateBtn.querySelector('.btn-loader');

    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
        generateBtn.disabled = true;
        console.log('Button set to loading state');
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        generateBtn.disabled = false;
        console.log('Button set to normal state');
    }
}

// Recent Jobs
async function loadRecentJobs() {
    console.log('Loading recent jobs');

    try {
        const response = await fetch(`${API_BASE_URL}/api/jobs`);
        const data = await response.json();

        console.log('Recent jobs loaded:', data.jobs.length);

        if (!data.jobs || data.jobs.length === 0) {
            jobsList.innerHTML = '<p class="empty-state">No videos generated yet. Create your first video above!</p>';
            return;
        }

        jobsList.innerHTML = data.jobs.map(job => `
            <div class="job-item">
                <div class="job-item-header">
                    <span class="status-badge ${job.status}">${job.status.toUpperCase()}</span>
                    <span class="job-item-meta">${formatDate(job.created_at)}</span>
                </div>
                <div class="job-item-prompt">${job.prompt}</div>
                ${job.status === 'completed' ? `
                    <a href="${job.video_url}" class="btn btn-success" download style="margin-top: 10px; padding: 8px 16px; font-size: 0.875rem;">
                        Download
                    </a>
                ` : ''}
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading recent jobs:', error);
    }
}

// Fetch available models
async function fetchAvailableModels() {
    console.log('Fetching available models');

    try {
        const response = await fetch(`${API_BASE_URL}/api/models`);
        const data = await response.json();

        console.log('Available models:', data.models);

        const modelSelect = document.getElementById('model');
        modelSelect.innerHTML = data.models.map(model => `
            <option value="${model.id}" ${model.id === 'animate-diff' ? 'selected' : ''}>
                ${model.name}
            </option>
        `).join('');

    } catch (error) {
        console.error('Error fetching models:', error);
    }
}

// Utilities
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
}

// Debug: Log API availability
fetch(`${API_BASE_URL}/health`)
    .then(res => res.json())
    .then(data => console.log('API Health Check:', data))
    .catch(err => console.error('API not available:', err));
