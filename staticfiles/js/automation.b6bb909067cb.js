class AutomationManager {
    constructor() {
        this.socket = null;
        this.taskId = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Platform selection
        document.querySelectorAll('.platform-card').forEach(card => {
            card.addEventListener('click', () => this.handlePlatformSelect(card));
        });

        // Action buttons
        document.querySelectorAll('.action-button').forEach(button => {
            button.addEventListener('click', () => this.handleActionSelect(button));
        });

        // Start button
        const startButton = document.getElementById('start-automation');
        if (startButton) {
            startButton.addEventListener('click', () => this.startAutomation());
        }
    }

    handlePlatformSelect(card) {
        // Update UI
        document.querySelectorAll('.platform-card').forEach(c => 
            c.classList.remove('selected'));
        card.classList.add('selected');
        
        // Show credentials form
        const credentialsForm = card.querySelector('.credentials-form');
        credentialsForm.classList.remove('hidden');
    }

    handleActionSelect(button) {
        document.querySelectorAll('.action-button').forEach(b => 
            b.classList.remove('selected'));
        button.classList.add('selected');
    }

    async startAutomation() {
        const platform = document.querySelector('.platform-card.selected')
            ?.dataset.platform;
        const action = document.querySelector('.action-button.selected')
            ?.dataset.action;
        const targetUrl = document.getElementById('target-url').value;
        const quantity = document.getElementById('quantity').value;

        if (!platform || !action || !targetUrl || !quantity) {
            this.showError('Please fill in all required fields');
            return;
        }

        try {
            const response = await fetch('/api/automation/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    platform,
                    action,
                    target_url: targetUrl,
                    quantity: parseInt(quantity)
                })
            });

            const data = await response.json();
            if (data.task_id) {
                this.taskId = data.task_id;
                this.connectWebSocket();
                this.showProgress();
            }
        } catch (error) {
            this.showError('Failed to start automation');
            console.error(error);
        }
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = new WebSocket(
            `${protocol}//${window.location.host}/ws/automation/${this.taskId}/`
        );

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateProgress(data);
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showError('Connection error');
        };
    }

    updateProgress(data) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-percentage');
        const actionText = document.getElementById('current-action');
        const actionLog = document.getElementById('action-log');

        if (progressBar && data.progress !== undefined) {
            progressBar.style.width = `${data.progress}%`;
            progressText.textContent = `${Math.round(data.progress)}%`;
        }

        if (actionText && data.action) {
            actionText.textContent = data.action;
        }

        if (actionLog && data.message) {
            const logEntry = document.createElement('div');
            logEntry.textContent = `${new Date().toLocaleTimeString()}: ${data.message}`;
            actionLog.appendChild(logEntry);
            actionLog.scrollTop = actionLog.scrollHeight;
        }

        if (data.type === 'complete') {
            this.handleCompletion(data);
        }
    }

    handleCompletion(data) {
        if (this.socket) {
            this.socket.close();
        }

        const completionMessage = document.createElement('div');
        completionMessage.className = 'text-lg font-semibold mt-4';
        completionMessage.textContent = data.success ? 
            'Automation completed successfully!' : 
            `Automation failed: ${data.error}`;
        
        document.getElementById('progress-container').appendChild(completionMessage);
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded';
        errorDiv.textContent = message;
        
        const container = document.querySelector('.container');
        container.insertBefore(errorDiv, container.firstChild);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }
}

// Initialize automation manager
document.addEventListener('DOMContentLoaded', () => {
    window.automationManager = new AutomationManager();
}); 