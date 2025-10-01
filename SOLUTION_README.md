# 🔧 EduMon Connection Fix - Complete Solution

## 🎯 Problem Summary

You were getting this error when running `python run_agent.py`:
```
Error de conexión al registrar: HTTPConnectionPool(host='190.84.119.196', port=8000): Max retries exceeded with url: /api/v1/register (Caused by ConnectTimeoutError(...))
```

**Root Cause**: The agent was trying to connect to a remote server (`190.84.119.196:8000`) that is not accessible or not running.

## ✅ Solutions (Choose One)

### 🚀 Option 1: Quick Fix - Simple Backend (Recommended)

This is the fastest way to get EduMon working:

1. **Run the simple setup:**
   ```bash
   python start_simple_backend.py
   ```

2. **Start the backend:**
   ```bash
   python simple_backend.py
   ```

3. **In another terminal, run the agent:**
   ```bash
   python run_agent.py
   ```

4. **Access the dashboard:**
   - Open: http://localhost:8000/dashboard?api_key=S1R4X

### 🐳 Option 2: Full Docker Setup

If you want the complete setup with PostgreSQL, pgAdmin, and Metabase:

1. **Make sure Docker Desktop is running**

2. **Run the automated fix:**
   ```bash
   python fix_edumon.py
   ```

3. **Or manually start the server:**
   ```bash
   python run_server.py
   ```

4. **Run the agent:**
   ```bash
   python run_agent.py
   ```

### 🔧 Option 3: Manual Backend Setup

If you prefer to set up the backend manually:

1. **Install backend dependencies:**
   ```bash
   cd edumon/backend
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export DATABASE_URL="sqlite:///./edumon.db"
   export EDUMON_API_KEY="S1R4X"
   export SECRET_KEY="your-secret-key"
   ```

3. **Start the backend:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Run the agent:**
   ```bash
   python run_agent.py
   ```

## 🔍 Testing Your Setup

Run this to test if everything is working:
```bash
python test_connection.py
```

## 🛠️ What Was Fixed

1. **Agent Configuration**: Updated `agent_config.json` to use `localhost` instead of `190.84.119.196`
2. **PyQt6 Warnings**: Removed unsupported `cursor: pointer` CSS property
3. **Docker Environment**: Created proper `.env` file for Docker setup
4. **Simple Backend**: Created a lightweight SQLite-based backend for quick testing

## 📊 Access Points

Once running, you can access:

- **Dashboard**: http://localhost:8000/dashboard?api_key=S1R4X
- **API Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs (if using full backend)

## 🔑 Default Credentials

- **API Key**: `S1R4X`
- **Classroom ID**: `Aula-1`

## 🚨 Troubleshooting

### Agent still can't connect?
1. Make sure the backend is running on port 8000
2. Check if `agent_config.json` has `"server_ip": "localhost"`
3. Verify no firewall is blocking port 8000

### Docker issues?
1. Make sure Docker Desktop is running
2. Try: `docker --version` and `docker info`
3. If Docker fails, use Option 1 (Simple Backend)

### "Unknown property cursor" warnings?
- These are fixed in the updated `gui_pyqt.py` file

## 📁 Files Created/Modified

- ✅ `agent_config.json` - Updated to use localhost
- ✅ `edumon/docker/.env` - Docker environment configuration
- ✅ `edumon/agent/ui/gui_pyqt.py` - Fixed CSS warnings
- 🆕 `simple_backend.py` - Lightweight backend for testing
- 🆕 `start_simple_backend.py` - Setup script for simple backend
- 🆕 `test_connection.py` - Connection testing utility
- 🆕 `fix_edumon.py` - Automated fix script

## 🎉 Success Indicators

You'll know it's working when:
1. ✅ `python test_connection.py` shows "Connection test PASSED!"
2. ✅ Agent shows "🟢 Conectado" status
3. ✅ Dashboard shows your connected agent
4. ✅ No more connection timeout errors

## 📞 Need Help?

If you're still having issues:
1. Run `python test_connection.py` and share the output
2. Check if any antivirus/firewall is blocking the connection
3. Try running as administrator if on Windows
4. Make sure no other application is using port 8000

---

**Happy monitoring! 🎓📊**