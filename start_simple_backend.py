#!/usr/bin/env python3
"""
Simple Backend Starter - No Docker Required
This script starts just the FastAPI backend with SQLite for quick testing.
"""
import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_backend_requirements():
    """Check if backend requirements are installed"""
    print("🔍 Checking backend requirements...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", "edumon/backend/requirements.txt"
            ])
            print("✅ Packages installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False
    else:
        print("✅ All required packages are installed")
        return True

def setup_sqlite_database():
    """Setup a simple SQLite database"""
    print("🗄️  Setting up SQLite database...")
    
    db_path = "edumon_simple.db"
    
    try:
        # Create a simple database with basic tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create basic tables (simplified version)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                hostname TEXT,
                username TEXT,
                classroom_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                device_id TEXT,
                cpu_percent REAL,
                mem_percent REAL,
                disk_percent REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✅ SQLite database created: {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def create_simple_main():
    """Create a simplified main.py for the backend"""
    print("📝 Creating simplified backend...")
    
    simple_main_content = '''#!/usr/bin/env python3
"""
Simplified EduMon Backend - SQLite Version
"""
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Configuration
API_KEY = "S1R4X"
DATABASE_PATH = "edumon_simple.db"

app = FastAPI(title="EduMon Simple Backend", version="2.0.0")

# Models
class RegisterRequest(BaseModel):
    device_id: str
    hostname: str
    username: str
    consent: bool
    classroom_id: Optional[str] = None

class HeartbeatRequest(BaseModel):
    device_id: str
    session_id: str
    metrics: Dict[str, Any]

class UnregisterRequest(BaseModel):
    device_id: str
    session_id: str
    reason: str = "user_request"

# Database helpers
def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

# Routes
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0-simple",
        "api_key_configured": True,
        "database": "sqlite",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/register")
async def register_agent(request: RegisterRequest, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    
    if not request.consent:
        raise HTTPException(status_code=400, detail="Consent required")
    
    session_id = str(uuid.uuid4())
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (id, device_id, hostname, username, classroom_id)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, request.device_id, request.hostname, request.username, request.classroom_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Agent registered: {request.device_id} ({request.username}@{request.hostname})")
        
        return {"session_id": session_id}
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/v1/heartbeat")
async def heartbeat(request: HeartbeatRequest, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update session last_heartbeat
        cursor.execute("""
            UPDATE sessions SET last_heartbeat = CURRENT_TIMESTAMP 
            WHERE id = ? AND device_id = ?
        """, (request.session_id, request.device_id))
        
        # Insert metrics
        metrics = request.metrics
        cursor.execute("""
            INSERT INTO metrics (session_id, device_id, cpu_percent, mem_percent, disk_percent)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.session_id, 
            request.device_id,
            metrics.get('cpu_percent', 0),
            metrics.get('mem_percent', 0),
            metrics.get('disk_percent', 0)
        ))
        
        conn.commit()
        conn.close()
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ Heartbeat error: {e}")
        raise HTTPException(status_code=500, detail="Heartbeat failed")

@app.post("/api/v1/unregister")
async def unregister_agent(request: UnregisterRequest, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions SET status = 'disconnected' 
            WHERE id = ? AND device_id = ?
        """, (request.session_id, request.device_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Agent unregistered: {request.device_id} (reason: {request.reason})")
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ Unregister error: {e}")
        raise HTTPException(status_code=500, detail="Unregister failed")

@app.get("/dashboard")
async def dashboard(api_key: str = None):
    if api_key != API_KEY:
        return HTMLResponse("<h1>Access Denied</h1><p>Invalid API key</p>", status_code=401)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get active sessions
        cursor.execute("""
            SELECT device_id, hostname, username, classroom_id, created_at, last_heartbeat
            FROM sessions WHERE status = 'active'
            ORDER BY last_heartbeat DESC
        """)
        sessions = cursor.fetchall()
        
        # Get recent metrics
        cursor.execute("""
            SELECT device_id, cpu_percent, mem_percent, disk_percent, timestamp
            FROM metrics 
            ORDER BY timestamp DESC LIMIT 10
        """)
        metrics = cursor.fetchall()
        
        conn.close()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EduMon Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .header {{ color: #333; }}
            </style>
        </head>
        <body>
            <h1 class="header">🎓 EduMon Dashboard</h1>
            <p><strong>Active Sessions:</strong> {len(sessions)}</p>
            
            <h2>Connected Agents</h2>
            <table>
                <tr>
                    <th>Device ID</th>
                    <th>Hostname</th>
                    <th>Username</th>
                    <th>Classroom</th>
                    <th>Connected</th>
                    <th>Last Heartbeat</th>
                </tr>
        """
        
        for session in sessions:
            html += f"""
                <tr>
                    <td>{session[0][:8]}...</td>
                    <td>{session[1]}</td>
                    <td>{session[2]}</td>
                    <td>{session[3] or 'N/A'}</td>
                    <td>{session[4]}</td>
                    <td>{session[5]}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Recent Metrics</h2>
            <table>
                <tr>
                    <th>Device ID</th>
                    <th>CPU %</th>
                    <th>Memory %</th>
                    <th>Disk %</th>
                    <th>Timestamp</th>
                </tr>
        """
        
        for metric in metrics:
            html += f"""
                <tr>
                    <td>{metric[0][:8]}...</td>
                    <td>{metric[1]:.1f}%</td>
                    <td>{metric[2]:.1f}%</td>
                    <td>{metric[3]:.1f}%</td>
                    <td>{metric[4]}</td>
                </tr>
            """
        
        html += """
            </table>
            <p><em>Refresh page to update data</em></p>
        </body>
        </html>
        """
        
        return HTMLResponse(html)
        
    except Exception as e:
        return HTMLResponse(f"<h1>Error</h1><p>{e}</p>", status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting EduMon Simple Backend...")
    print("📊 Dashboard: http://localhost:8000/dashboard?api_key=S1R4X")
    print("❤️  Health: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    try:
        with open("simple_backend.py", "w") as f:
            f.write(simple_main_content)
        print("✅ Simple backend created: simple_backend.py")
        return True
    except Exception as e:
        print(f"❌ Error creating backend: {e}")
        return False

def main():
    print("🎓 EduMon Simple Backend Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_backend_requirements():
        print("❌ Failed to install requirements")
        return 1
    
    # Setup database
    if not setup_sqlite_database():
        print("❌ Failed to setup database")
        return 1
    
    # Create simple backend
    if not create_simple_main():
        print("❌ Failed to create backend")
        return 1
    
    print("\n✅ Setup complete!")
    print("\n🚀 To start the backend:")
    print("   python simple_backend.py")
    print("\n📊 Dashboard will be available at:")
    print("   http://localhost:8000/dashboard?api_key=S1R4X")
    print("\n🤖 Then run the agent:")
    print("   python run_agent.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())