const express = require('express');
const path = require('path');
const app = express();

// Serve static files
app.use(express.static('.'));

// Handle POST requests for speed test
app.post('/', express.json(), (req, res) => {
    res.json({ status: 'success' });
});

// Serve index.html for all other routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 