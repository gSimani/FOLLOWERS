// Error Monitor Module
(function() {
    let errorCount = 0;
    let lastError = null;

    // Monitor JavaScript errors
    window.addEventListener('error', function(event) {
        errorCount++;
        lastError = {
            message: event.message,
            source: event.filename,
            line: event.lineno,
            column: event.colno,
            timestamp: new Date(),
            stack: event.error ? event.error.stack : null
        };
        
        // Update health status
        const healthStatus = document.getElementById('health-status');
        if (healthStatus) {
            healthStatus.textContent = `Errors: ${errorCount}`;
            healthStatus.className = errorCount > 0 ? 'status-badge error' : 'status-badge success';
        }
        
        // Log error details
        console.error('Error detected:', lastError);
    });

    // Monitor unhandled promise rejections
    window.addEventListener('unhandledrejection', function(event) {
        errorCount++;
        lastError = {
            message: event.reason,
            type: 'Promise Rejection',
            timestamp: new Date(),
            stack: event.reason.stack
        };
        
        // Update health status
        const healthStatus = document.getElementById('health-status');
        if (healthStatus) {
            healthStatus.textContent = `Errors: ${errorCount}`;
            healthStatus.className = 'status-badge error';
        }
        
        // Log error details
        console.error('Unhandled Promise Rejection:', lastError);
    });

    // Monitor network errors
    window.addEventListener('offline', function() {
        const healthStatus = document.getElementById('health-status');
        if (healthStatus) {
            healthStatus.textContent = 'Network Offline';
            healthStatus.className = 'status-badge error';
        }
    });

    window.addEventListener('online', function() {
        const healthStatus = document.getElementById('health-status');
        if (healthStatus) {
            healthStatus.textContent = errorCount > 0 ? `Errors: ${errorCount}` : 'Healthy';
            healthStatus.className = errorCount > 0 ? 'status-badge error' : 'status-badge success';
        }
    });

    // Monitor performance
    setInterval(function() {
        const performanceStatus = document.getElementById('performance-status');
        if (performanceStatus) {
            const memory = performance.memory ? 
                Math.round(performance.memory.usedJSHeapSize / 1048576) : 
                'N/A';
            performanceStatus.textContent = `Memory: ${memory}MB`;
        }
    }, 5000);
})(); 