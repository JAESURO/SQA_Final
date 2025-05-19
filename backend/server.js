const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');
const cors = require('cors');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Serve static files from the root directory
app.use(express.static(path.join(__dirname, '..')));

// Serve index.html for the root route
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'index.html'));
});

// Serve login.html for the login route
app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'login.html'));
});

// Serve register.html for the register route
app.get('/register', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'register.html'));
});

const dbPath = path.join(__dirname, 'users.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error connecting to database:', err.message);
    } else {
        console.log('Connected to the users database.');
    }
});

db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)`, (err) => {
    if (err) {
        console.error('Error creating users table:', err.message);
    } else {
        console.log('Users table ready.');
    }
});

db.run(`CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    completed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)`, (err) => {
    if (err) {
        console.error('Error creating tasks table:', err.message);
    } else {
        console.log('Tasks table ready.');
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.post('/register', async (req, res) => {
    const { email, password } = req.body;
    
    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        
        db.run('INSERT INTO users (email, password) VALUES (?, ?)',
            [email, hashedPassword],
            function(err) {
                if (err) {
                    if (err.message.includes('UNIQUE constraint failed')) {
                        return res.status(400).json({ error: 'Email already exists' });
                    }
                    return res.status(500).json({ error: 'Error creating user' });
                }
                res.status(201).json({ message: 'User created successfully' });
            }
        );
    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ error: 'Error hashing password' });
    }
});

app.post('/login', (req, res) => {
    const { email, password } = req.body;
    
    db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
        if (err) {
            console.error('Login error:', err);
            return res.status(500).json({ error: 'Error finding user' });
        }
        if (!user) {
            return res.status(400).json({ error: 'User not found' });
        }
        
        try {
            const match = await bcrypt.compare(password, user.password);
            if (match) {
                res.json({ message: 'Login successful', userId: user.id });
            } else {
                res.status(400).json({ error: 'Invalid password' });
            }
        } catch (error) {
            console.error('Password comparison error:', error);
            res.status(500).json({ error: 'Error comparing passwords' });
        }
    });
});

app.get('/tasks/:userId', (req, res) => {
    const userId = req.params.userId;
    
    db.all('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC', [userId], (err, tasks) => {
        if (err) {
            console.error('Error fetching tasks:', err);
            return res.status(500).json({ error: 'Error fetching tasks' });
        }
        res.json(tasks);
    });
});

app.post('/tasks', (req, res) => {
    const { userId, text } = req.body;
    
    if (!userId || !text) {
        return res.status(400).json({ error: 'User ID and task text are required' });
    }
    
    db.run('INSERT INTO tasks (user_id, text) VALUES (?, ?)',
        [userId, text],
        function(err) {
            if (err) {
                console.error('Error creating task:', err);
                return res.status(500).json({ error: 'Error creating task' });
            }
            res.status(201).json({ 
                id: this.lastID,
                user_id: userId,
                text: text,
                completed: 0,
                created_at: new Date().toISOString()
            });
        }
    );
});

app.patch('/tasks/:taskId', (req, res) => {
    const taskId = req.params.taskId;
    const { completed } = req.body;
    
    db.run('UPDATE tasks SET completed = ? WHERE id = ?',
        [completed ? 1 : 0, taskId],
        function(err) {
            if (err) {
                console.error('Error updating task:', err);
                return res.status(500).json({ error: 'Error updating task' });
            }
            res.json({ message: 'Task updated successfully' });
        }
    );
});

app.delete('/tasks/:taskId', (req, res) => {
    const taskId = req.params.taskId;
    
    db.run('DELETE FROM tasks WHERE id = ?', [taskId], function(err) {
        if (err) {
            console.error('Error deleting task:', err);
            return res.status(500).json({ error: 'Error deleting task' });
        }
        res.json({ message: 'Task deleted successfully' });
    });
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something broke!' });
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Server running at http://localhost:${port}`);
}); 