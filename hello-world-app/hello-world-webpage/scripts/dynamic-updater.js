// Dynamic Updater Module
(function() {
    let updateInterval;
    const UPDATE_FREQUENCY = 5000; // 5 seconds

    function startUpdates() {
        if (!updateInterval) {
            updateInterval = setInterval(updateDynamicContent, UPDATE_FREQUENCY);
            console.log('Dynamic updates started');
        }
    }

    function stopUpdates() {
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
            console.log('Dynamic updates stopped');
        }
    }

    function updateDynamicContent() {
        // Update timestamp
        const timestamp = document.getElementById('timestamp');
        if (timestamp) {
            timestamp.textContent = `Updated: ${new Date().toLocaleString()}`;
        }

        // Update performance metrics
        const performanceStatus = document.getElementById('performance-status');
        if (performanceStatus) {
            const now = performance.now();
            const memory = performance.memory ? 
                `Memory: ${Math.round(performance.memory.usedJSHeapSize / 1048576)}MB` : 
                'Performance metrics not available';
            performanceStatus.textContent = memory;
        }

        // Update health status
        const healthStatus = document.getElementById('health-status');
        if (healthStatus) {
            const errors = window.pageMonitor ? 
                window.pageMonitor.getHealthReport().errors.length : 
                0;
            
            if (errors > 0) {
                healthStatus.textContent = `Issues Found (${errors})`;
                healthStatus.className = 'status-badge error';
            } else if (!navigator.onLine) {
                healthStatus.textContent = 'Offline';
                healthStatus.className = 'status-badge warning';
            } else {
                healthStatus.textContent = 'Healthy';
                healthStatus.className = 'status-badge success';
            }
        }
    }

    // Start updates when page loads
    document.addEventListener('DOMContentLoaded', startUpdates);

    // Pause updates when page is not visible
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopUpdates();
        } else {
            startUpdates();
            // Immediate update when page becomes visible
            updateDynamicContent();
        }
    });

    // Public API
    window.dynamicUpdater = {
        start: startUpdates,
        stop: stopUpdates,
        update: updateDynamicContent
    };
})(); 