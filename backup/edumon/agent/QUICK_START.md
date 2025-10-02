# EduMon Agent - Quick Start Guide

## 🚀 Quick Setup (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Server URL
Run the configuration script:

**Windows:**
```cmd
update_config.bat
```

**Linux/Mac:**
```bash
./update_config.sh
```

**Or manually:** Edit `config.json` and replace `<YOUR_NGROK_URL>` with your ngrok URL.

### Step 3: Run the Agent
**Windows:**
```cmd
run_agent.bat
```

**Linux/Mac:**
```bash
./run_agent.sh
```

**Or manually:**
```bash
python main_simple.py
```

## 📋 What You Need

1. **Your ngrok URL** - Something like: `https://1234-5678-9abc-def0.ngrok-free.app`
2. **Python 3.10+** with pip
3. **Internet connection**

## 🔧 Configuration File

The `config.json` file should look like this after configuration:

```json
{
  "server_url": "https://your-ngrok-url.ngrok-free.app",
  "api_key": "S1R4X"
}
```

## 🎯 Expected Output

When running successfully, you'll see:

```
🎓 EduMon Agent - Versión Simple
========================================

🔗 Conectando con servidor: https://your-ngrok-url.ngrok-free.app
✅ Registro exitoso. Session ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

🚀 AGENTE INICIADO
========================================
📊 Métricas enviadas - CPU: 15.2% RAM: 45.8%
```

## 🛑 Stopping the Agent

Press `Ctrl+C` to stop the agent safely. It will automatically unregister from the server.

## 🔍 Troubleshooting

- **"Connection refused"**: Check that your Node.js server is running and ngrok is active
- **"Module not found"**: Run `pip install -r requirements.txt`
- **"Config file not found"**: Make sure you're in the `backup/edumon/agent` directory

## 📁 Files Overview

- `config.json` - Main configuration file
- `main_simple.py` - Simple agent (recommended)
- `main.py` - Full agent with GUI support
- `update_config.py` - Configuration helper script
- `requirements.txt` - Python dependencies

---

**Need help?** Check the main `EDUMON_SETUP_GUIDE.md` in the project root for detailed instructions.