# SecurAula-AI Server Management Guide

## Quick Start

### Option 1: Use the automated script (Recommended)
```bash
start_server.bat
```
This script will:
- Check if port 3000 is available
- Offer to kill any conflicting processes
- Start the server automatically

### Option 2: Manual start
```bash
node server.js
```

## If Port 3000 is Busy

### Solution 1: Kill the conflicting process
1. Find the process using port 3000:
   ```bash
   netstat -ano | findstr :3000
   ```
2. Kill the process (replace PID with actual process ID):
   ```bash
   taskkill /PID <PID> /F
   ```

### Solution 2: Use a different port
```bash
# Windows
set PORT=3001 && node server.js

# Linux/Mac
PORT=3001 node server.js
```

## Server Features

✅ **Improved Error Handling**: Clear error messages when port is busy
✅ **Graceful Shutdown**: Press Ctrl+C to stop the server properly
✅ **Port Configuration**: Use PORT environment variable to change port
✅ **Better Logging**: Enhanced console output with emojis and clear formatting

## API Endpoints

- `GET /` - Dashboard interface
- `POST /api/v1/register` - Device registration
- `POST /api/v1/heartbeat` - Device heartbeat
- `POST /api/v1/unregister` - Device unregistration
- `GET /api/v1/devices` - Get connected devices

## Files

- `server.js` - Main server file (improved version)
- `server_original.js` - Original server backup
- `start_server.bat` - Automated startup script
- `package.json` - Node.js dependencies

## Troubleshooting

### "EADDRINUSE" Error
This means port 3000 is already in use. Use the solutions above.

### "Cannot find module" Error
Run `npm install` to install dependencies.

### Server won't start
1. Check if Node.js is installed: `node --version`
2. Check if dependencies are installed: `ls node_modules`
3. Try using a different port: `set PORT=3001 && node server.js`