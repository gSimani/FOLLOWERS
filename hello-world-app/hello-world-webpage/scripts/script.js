// Update timestamp
function updateTimestamp() {
    const timestamp = document.getElementById('timestamp');
    timestamp.textContent = `Updated: ${new Date().toLocaleString()}`;
}

// Add test message
function addTestMessage() {
    const input = document.getElementById('messageInput');
    const messages = document.getElementById('messages');
    
    if (input.value.trim()) {
        const message = document.createElement('div');
        message.className = 'message';
        message.innerHTML = `
            <div class="message-content">
                <span class="message-text">${input.value}</span>
                <span class="message-time">${new Date().toLocaleTimeString()}</span>
            </div>
            <button class="delete-message" onclick="this.parentElement.remove()">×</button>
        `;
        messages.appendChild(message);
        input.value = '';
        
        // Scroll to bottom of message list
        messages.scrollTop = messages.scrollHeight;
    }
}

// Clear all messages
function clearMessages() {
    const messages = document.getElementById('messages');
    messages.innerHTML = '';
}

// Check server status
function checkServerStatus() {
    const serverInfo = document.querySelector('.status-card:first-child .status-info p');
    serverInfo.textContent = 'Checking...';
    
    // Get current hostname
    const hostname = window.location.hostname;
    const isProduction = hostname === 'www.yidbiz.com' || hostname === 'yidbiz.com';
    const isVercel = hostname.includes('vercel.app');
    
    // Simulate server check with real status
    setTimeout(() => {
        const isOnline = true; // We know we're online if the page loaded
        let statusText;
        
        if (isProduction) {
            statusText = 'Running on YidBiz.com';
        } else if (isVercel) {
            statusText = 'Running on Vercel';
        } else if (hostname === 'localhost') {
            statusText = 'Running on localhost:8000';
        } else {
            statusText = `Running on ${hostname}`;
        }
        
        serverInfo.textContent = isOnline ? statusText : 'Connection issues detected';
        serverInfo.style.color = isOnline ? '#666' : '#dc3545';
        
        // Update environment badge
        const envBadge = document.querySelector('.environment-badge');
        if (envBadge) {
            if (isProduction) {
                envBadge.textContent = 'Production Environment';
                envBadge.style.backgroundColor = '#4CAF50';
            } else if (isVercel) {
                envBadge.textContent = 'Staging Environment';
                envBadge.style.backgroundColor = '#FF9800';
            } else {
                envBadge.textContent = 'Development Environment';
                envBadge.style.backgroundColor = '#2196F3';
            }
        }
    }, 1000);
}

// Update performance metrics
function updatePerformanceMetrics() {
    const performanceStatus = document.getElementById('performance-status');
    const metrics = {
        pageLoad: Math.round(performance.now()),
        memory: performance.memory ? 
            Math.round(performance.memory.usedJSHeapSize / 1048576) : 
            null
    };
    
    performanceStatus.innerHTML = `
        Page Load: ${metrics.pageLoad}ms<br>
        Memory: ${metrics.memory ? metrics.memory + 'MB' : 'N/A'}
    `;
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    // Set initial timestamp
    updateTimestamp();
    
    // Update timestamp every minute
    setInterval(updateTimestamp, 60000);
    
    // Add message on Enter key
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addTestMessage();
        }
    });
    
    // Add clear messages button
    const testSection = document.querySelector('.test-section .test-controls');
    const clearButton = document.createElement('button');
    clearButton.className = 'modern-button secondary';
    clearButton.textContent = 'Clear Messages';
    clearButton.onclick = clearMessages;
    testSection.appendChild(clearButton);
    
    // Initialize server status check
    checkServerStatus();
    setInterval(checkServerStatus, 30000); // Check every 30 seconds
    
    // Initialize performance metrics
    updatePerformanceMetrics();
    setInterval(updatePerformanceMetrics, 5000); // Update every 5 seconds
    
    // Add click handlers for status cards
    document.querySelectorAll('.status-card').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', () => {
            const info = card.querySelector('.status-info');
            const title = info.querySelector('h3').textContent;
            
            switch(title) {
                case 'Server Status':
                    checkServerStatus();
                    break;
                case 'Performance':
                    updatePerformanceMetrics();
                    break;
                case 'Page Health':
                    window.pageMonitor.checkPageHealth();
                    showHealthReport();
                    break;
            }
            
            // Add click animation
            card.style.transform = 'scale(0.98)';
            setTimeout(() => card.style.transform = '', 100);
        });
    });
});