# Web Application with Authentication

A full-stack web application featuring user authentication, built with Node.js, Express, and modern web technologies.

## Features

- User authentication (login/register)
- Responsive design
- Docker containerization
- Express.js backend
- Modern frontend with HTML, CSS, and JavaScript

## Run

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up build
   ```

3. Start the frontend using app.js:
   ```bash
   node app.js
   ```

## Project Structure

```
├── backend/           # Backend server code
├── node_modules/      # Node.js dependencies
├── app.js            # Main application file
├── index.html        # Main page
├── login.html        # Login page
├── register.html     # Registration page
├── styles.css        # Main styles
├── login-styles.css  # Login page styles
├── script.js         # Main frontend logic
├── login.js          # Login functionality
├── register.js       # Registration functionality
├── docker-compose.yml # Docker configuration
└── package.json      # Project dependencies and scripts
```