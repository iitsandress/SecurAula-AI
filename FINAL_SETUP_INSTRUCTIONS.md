# 🎯 EduMon Agent Configuration - FINAL INSTRUCTIONS

## ✅ What Has Been Completed

### 1. **Agent Configuration**
- ✅ Updated `backup/edumon/agent/config.json` with your ngrok URL: `https://cae7ccde57d5.ngrok-free.app`
- ✅ API key correctly set to "S1R4X"
- ✅ Python dependencies installed (requests, psutil)
- ✅ Created Windows-compatible agent version (`main_windows.py`)

### 2. **Server Enhancement**
- ✅ Updated `new_nodejs_server/server.js` with complete API endpoints:
  - `POST /api/v1/register` - Device registration
  - `POST /api/v1/heartbeat` - Metrics collection
  - `POST /api/v1/unregister` - Device disconnection
  - `GET /api/v1/devices` - Dashboard data
- ✅ Added API key validation middleware
- ✅ In-memory device storage and session management

### 3. **Helper Scripts Created**
- ✅ `test_agent.py` - Complete agent functionality test
- ✅ `main_windows.py` - Unicode-free agent for Windows
- ✅ `simple_test.py` - Basic connection test
- ✅ Various configuration and startup scripts

## 🚀 Next Steps (What You Need To Do)

### Step 1: Restart Your Node.js Server
**IMPORTANT**: You need to restart your Node.js server to apply the API changes.

1. **Stop the current server** (Ctrl+C in the terminal where it's running)
2. **Start it again**:
   ```bash
   cd new_nodejs_server
   node server.js
   ```

You should see:
```
Server listening on http://localhost:3000
API endpoints available:
  POST /api/v1/register
  POST /api/v1/heartbeat
  POST /api/v1/unregister
  GET  /api/v1/devices
```

### Step 2: Verify Server is Working
Run this test:
```bash
python test_new_server.py
```

You should see successful API responses instead of 404 errors.

### Step 3: Run the EduMon Agent
```bash
cd backup/edumon/agent
python main_windows.py
```

When prompted for consent, type `yes` and press Enter.

## 🎯 Expected Results

### Server Console Output:
```
Device registered: COMPUTER-NAME (username) - Session: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Heartbeat from COMPUTER-NAME: CPU 15.2% RAM 45.8%
Heartbeat from COMPUTER-NAME: CPU 12.1% RAM 47.3%
...
```

### Agent Console Output:
```
EduMon Agent - Simple Version
========================================

EDUMON - CONSENT FOR EDUCATIONAL MONITORING
============================================================
Do you accept to participate in this monitoring session? (yes/no): yes

Connecting to server: https://cae7ccde57d5.ngrok-free.app
Registration successful. Session ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

AGENT STARTED
========================================
Device ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Server: https://cae7ccde57d5.ngrok-free.app
Classroom: Aula-1
Interval: 15 seconds

Press Ctrl+C to stop
========================================

Metrics sent - CPU: 15.2% RAM: 45.8%
Metrics sent - CPU: 12.1% RAM: 47.3%
...
```

### Dashboard Access:
Open `https://cae7ccde57d5.ngrok-free.app` in your browser to see connected devices.

## 🔧 Configuration Summary

### Current Configuration (`backup/edumon/agent/config.json`):
```json
{
  "server_url": "https://cae7ccde57d5.ngrok-free.app",
  "api_key": "S1R4X",
  "classroom_id": "Aula-1",
  "heartbeat_seconds": 15,
  "verify_ssl": true,
  "timeout_seconds": 10
}
```

### Your ngrok URL:
- **Public URL**: `https://cae7ccde57d5.ngrok-free.app`
- **Local URL**: `http://localhost:3000`

## 🛠️ Troubleshooting

### If Agent Shows "Registration failed: 404":
- ❌ Server not restarted with new API endpoints
- ✅ **Solution**: Restart your Node.js server

### If Agent Shows "Connection refused":
- ❌ ngrok tunnel is down
- ✅ **Solution**: Check ngrok is still running

### If Agent Shows Unicode errors:
- ❌ Using `main_simple.py` on Windows
- ✅ **Solution**: Use `python main_windows.py` instead

### If Server Shows "Cannot find module 'uuid'":
- ❌ Missing dependency (shouldn't happen with current code)
- ✅ **Solution**: The server now uses built-in crypto instead

## 📁 File Structure Summary

```
SecurAula-AI/
├── backup/edumon/agent/
│   ├── config.json              # ✅ CONFIGURED with your ngrok URL
│   ├── main_windows.py          # ✅ Windows-compatible agent
│   ├── test_agent.py           # ✅ Full functionality test
│   ├── simple_test.py          # ✅ Basic connection test
│   └── requirements.txt        # ✅ Python dependencies
├── new_nodejs_server/
│   ├── server.js               # ✅ UPDATED with API endpoints
│   └── dashboard.html          # ✅ Dashboard interface
└── test_new_server.py          # ✅ Server API test
```

## 🎉 Success Criteria

✅ **Server restarted** and shows API endpoints in console  
✅ **Agent connects** and shows "Registration successful"  
✅ **Heartbeats sent** every 15 seconds with CPU/RAM metrics  
✅ **Dashboard accessible** at your ngrok URL  
✅ **Device appears** in dashboard with live metrics  

---

**🚨 CRITICAL**: The most important step is restarting your Node.js server to enable the API endpoints. Everything else is already configured and ready to go!