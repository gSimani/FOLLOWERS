const chokidar = require('chokidar');
const { exec } = require('child_process');

// Initialize watcher
const watcher = chokidar.watch('.', {
    ignored: /(^|[\/\\])\../, // ignore dotfiles
    persistent: true
});

// Function to execute git commands
const gitPush = () => {
    exec('git add . && git commit -m "Auto-commit: File changes detected" && git push', (error, stdout, stderr) => {
        if (error) {
            console.error(`Error: ${error}`);
            return;
        }
        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
    });
};

// Add event listeners
watcher
    .on('change', path => {
        console.log(`File ${path} has been changed`);
        gitPush();
    })
    .on('add', path => {
        console.log(`File ${path} has been added`);
        gitPush();
    });

console.log('Watching for file changes...'); 