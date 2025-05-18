const express = require('express');
const path = require('path');
const app = express();
const port = 8080;

app.use(express.static(__dirname));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'login.html'));
});

app.listen(port, () => {
    console.log(`Web server running at http://localhost:${port}`);
}); 