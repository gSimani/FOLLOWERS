// Utility functions
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

const showNotification = (message, type = 'success') => {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
};

// URL Management
const loadSavedUrls = async () => {
    try {
        const platform = document.body.dataset.platform;
        const response = await fetch(`/automation/${platform}/urls/`);
        const data = await response.json();
        
        const urlList = document.querySelector('#url-list');
        urlList.innerHTML = '';
        
        data.urls.forEach((url, index) => {
            const urlItem = document.createElement('div');
            urlItem.className = 'flex items-center space-x-2';
            urlItem.innerHTML = `
                <span class="text-gray-500">${index + 1}.</span>
                <input type="text" value="${url.url}" class="flex-1 px-3 py-2 border rounded-lg" readonly>
                <button onclick="deleteUrl(${url.id})" class="text-red-500 hover:text-red-700">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            urlList.appendChild(urlItem);
        });
    } catch (error) {
        showNotification('Failed to load saved URLs', 'error');
    }
};

const saveUrl = async (url) => {
    try {
        const platform = document.body.dataset.platform;
        const response = await fetch(`/automation/${platform}/urls/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `url=${encodeURIComponent(url)}`
        });
        
        const data = await response.json();
        if (response.ok) {
            showNotification('URL saved successfully');
            loadSavedUrls();
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
};

const deleteUrl = async (urlId) => {
    if (!confirm('Are you sure you want to delete this URL?')) return;
    
    try {
        const platform = document.body.dataset.platform;
        const response = await fetch(`/automation/${platform}/urls/${urlId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (response.ok) {
            showNotification('URL deleted successfully');
            loadSavedUrls();
        } else {
            const data = await response.json();
            throw new Error(data.error);
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
};

// Task Progress Tracking
let progressPollingInterval = null;

const startProgressPolling = (taskId) => {
    // Clear any existing polling
    stopProgressPolling();
    
    // Start polling every 2 seconds
    progressPollingInterval = setInterval(() => {
        fetchTaskProgress(taskId);
    }, 2000);
};

const stopProgressPolling = () => {
    if (progressPollingInterval) {
        clearInterval(progressPollingInterval);
        progressPollingInterval = null;
    }
};

const fetchTaskProgress = async (taskId) => {
    try {
        const response = await fetch(`/automation/tasks/${taskId}/progress/`);
        const data = await response.json();
        
        if (response.ok) {
            updateProgressUI(data);
            
            // Stop polling if task is completed or failed
            if (['completed', 'failed', 'cancelled'].includes(data.status)) {
                stopProgressPolling();
            }
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showNotification(error.message, 'error');
        stopProgressPolling();
    }
};

const updateProgressUI = (progressData) => {
    // Update progress bar
    const progressBar = document.querySelector('#task-progress-bar');
    if (progressBar) {
        progressBar.style.width = `${progressData.progress_percentage}%`;
        progressBar.setAttribute('aria-valuenow', progressData.progress_percentage);
    }
    
    // Update status
    const statusBadge = document.querySelector('#task-status');
    if (statusBadge) {
        statusBadge.textContent = progressData.status;
        statusBadge.className = `px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
            progressData.status === 'completed' ? 'bg-green-100 text-green-800' :
            progressData.status === 'failed' ? 'bg-red-100 text-red-800' :
            progressData.status === 'running' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
        }`;
    }
    
    // Update counts
    const counts = document.querySelector('#task-counts');
    if (counts) {
        counts.innerHTML = `
            <span class="text-gray-500">Processed: ${progressData.total_processed}</span>
            <span class="text-green-500">Succeeded: ${progressData.total_succeeded}</span>
            <span class="text-red-500">Failed: ${progressData.total_failed}</span>
        `;
    }
    
    // Update progress logs
    const logsList = document.querySelector('#progress-logs');
    if (logsList && progressData.progress_logs.length > 0) {
        logsList.innerHTML = progressData.progress_logs.map(log => `
            <div class="py-2 border-b last:border-b-0">
                <div class="flex justify-between items-center">
                    <span class="font-medium">${log.target_username}</span>
                    <span class="${
                        log.status === 'success' ? 'text-green-500' : 'text-red-500'
                    }">${log.status}</span>
                </div>
                ${log.error_message ? `
                    <p class="mt-1 text-sm text-red-500">${log.error_message}</p>
                ` : ''}
                <p class="text-xs text-gray-500">${new Date(log.created_at).toLocaleString()}</p>
            </div>
        `).join('');
    }
    
    // Show error message if any
    if (progressData.error_message) {
        const errorDiv = document.querySelector('#task-error');
        if (errorDiv) {
            errorDiv.textContent = progressData.error_message;
            errorDiv.classList.remove('hidden');
        }
    }
};

// Automation
const createAutomation = async (event) => {
    event.preventDefault();
    
    const platform = document.body.dataset.platform;
    const action = document.querySelector('.action-btn.border-indigo-500')?.dataset.action;
    const profileUrl = document.querySelector('#profile-url').value;
    const target = document.querySelector('input[name="target"]:checked').value;
    const quantity = document.querySelector('#quantity').value;
    
    if (!action || !profileUrl || !target) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/automation/${platform}/automate/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: new URLSearchParams({
                action,
                profile_url: profileUrl,
                target,
                quantity
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            showNotification('Automation task created successfully');
            // Save URL for future use
            await saveUrl(profileUrl);
            
            // Start progress polling
            startProgressPolling(data.task_id);
            
            // Show progress modal
            toggleModal('progress-modal');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load saved URLs when URL modal is opened
    document.querySelector('#url-modal').addEventListener('show.bs.modal', loadSavedUrls);
    
    // Handle form submission
    document.querySelector('#automation-form').addEventListener('submit', createAutomation);
    
    // Handle custom quantity input
    const quantitySelect = document.querySelector('#quantity');
    quantitySelect.addEventListener('change', (event) => {
        if (event.target.value === 'custom') {
            const customQuantity = prompt('Enter custom quantity (max 1000):', '50');
            if (customQuantity) {
                const quantity = parseInt(customQuantity);
                if (isNaN(quantity) || quantity < 1 || quantity > 1000) {
                    showNotification('Please enter a valid quantity between 1 and 1000', 'error');
                    event.target.value = '50';
                } else {
                    const option = document.createElement('option');
                    option.value = quantity;
                    option.textContent = `${quantity} users`;
                    option.selected = true;
                    event.target.appendChild(option);
                }
            } else {
                event.target.value = '50';
            }
        }
    });
    
    // Handle paste button
    document.querySelector('.fa-paste').parentElement.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            document.querySelector('#profile-url').value = text;
        } catch (error) {
            showNotification('Failed to paste from clipboard', 'error');
        }
    });
}); 