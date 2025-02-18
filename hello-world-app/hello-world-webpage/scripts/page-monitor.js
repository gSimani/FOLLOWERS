// Page Monitor Module
window.pageMonitor = (function() {
    let logs = [];
    let errors = [];
    let warnings = [];
    let startTime = Date.now();
    let lastCheck = null;

    // Initialize error monitoring
    window.addEventListener('error', function(event) {
        errors.push({
            message: event.message,
            source: event.filename,
            line: event.lineno,
            timestamp: new Date()
        });
        updateDebugOutput();
    });

    // Monitor console warnings
    const originalWarn = console.warn;
    console.warn = function() {
        warnings.push({
            message: Array.from(arguments).join(' '),
            timestamp: new Date()
        });
        originalWarn.apply(console, arguments);
        updateDebugOutput();
    };

    function updateDebugOutput() {
        const output = document.getElementById('debug-output');
        if (output) {
            output.innerHTML = `Latest Events:
${errors.slice(-3).map(e => `Error: ${e.message}`).join('\n')}
${warnings.slice(-3).map(w => `Warning: ${w.message}`).join('\n')}`;
        }
    }

    function checkPageHealth() {
        lastCheck = new Date();
        const memoryUsage = performance.memory ? 
            Math.round(performance.memory.usedJSHeapSize / 1048576) + 'MB' : 
            'Not available';
        
        console.log(`Health Check Results:
- Memory Usage: ${memoryUsage}
- Errors: ${errors.length}
- Warnings: ${warnings.length}
- Uptime: ${Math.floor((Date.now() - startTime) / 1000)}s`);
        
        updateDebugOutput();
    }

    function getHealthReport() {
        const localStorageSize = Object.keys(localStorage).reduce((size, key) => {
            return size + (localStorage[key].length * 2);
        }, 0);

        return {
            errors: errors,
            warnings: warnings,
            uptime: Date.now() - startTime,
            lastCheck: lastCheck,
            totalLogs: logs.length,
            localStorage: {
                size: `${Math.round(localStorageSize / 1024)}KB`,
                items: Object.keys(localStorage).length
            }
        };
    }

    function clearLogs() {
        logs = [];
        errors = [];
        warnings = [];
        updateDebugOutput();
        console.log('Logs cleared');
    }

    // Public API
    return {
        checkPageHealth: checkPageHealth,
        getHealthReport: getHealthReport,
        clearLogs: clearLogs
    };
})(); 