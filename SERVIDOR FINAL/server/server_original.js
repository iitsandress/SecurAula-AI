const express = require('express');
const ngrok = require('ngrok');
const path = require('path');
const crypto = require('crypto');

// Simple UUID generator using crypto
const uuidv4 = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(__dirname));

// API Key validation middleware
const validateApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  if (apiKey !== 'S1R4X') {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  next();
};

// In-memory storage for demo purposes
const connectedDevices = new Map();
const sessions = new Map();

// Dashboard route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// API Routes
app.post('/api/v1/register', validateApiKey, (req, res) => {
  try {
    const { device_id, hostname, username, consent, classroom_id } = req.body;
    
    if (!device_id || !hostname || !username || consent !== true) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    const session_id = uuidv4();
    const timestamp = new Date().toISOString();
    
    const deviceInfo = {
      device_id,
      hostname,
      username,
      classroom_id,
      session_id,
      registered_at: timestamp,
      last_heartbeat: timestamp,
      status: 'connected'
    };
    
    connectedDevices.set(device_id, deviceInfo);
    sessions.set(session_id, deviceInfo);
    
    console.log(`Device registered: ${hostname} (${username}) - Session: ${session_id}`);
    
    res.json({
      session_id,
      status: 'registered',
      message: 'Device registered successfully'
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/v1/heartbeat', validateApiKey, (req, res) => {
  try {
    const { device_id, session_id, metrics } = req.body;
    
    if (!device_id || !session_id || !metrics) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    const device = connectedDevices.get(device_id);
    if (!device || device.session_id !== session_id) {
      return res.status(404).json({ error: 'Device not found or invalid session' });
    }
    
    // Update device info with latest metrics
    device.last_heartbeat = new Date().toISOString();
    device.metrics = metrics;
    device.status = 'active';
    
    connectedDevices.set(device_id, device);
    
    console.log(`Heartbeat from ${device.hostname}: CPU ${metrics.cpu_percent}% RAM ${metrics.mem_percent}%`);
    
    res.json({
      status: 'received',
      message: 'Heartbeat processed successfully'
    });
  } catch (error) {
    console.error('Heartbeat error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/v1/unregister', validateApiKey, (req, res) => {
  try {
    const { device_id, session_id, reason } = req.body;
    
    if (!device_id || !session_id) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    const device = connectedDevices.get(device_id);
    if (device && device.session_id === session_id) {
      device.status = 'disconnected';
      device.disconnected_at = new Date().toISOString();
      device.disconnect_reason = reason || 'unknown';
      
      console.log(`Device unregistered: ${device.hostname} - Reason: ${reason}`);
    }
    
    res.json({
      status: 'unregistered',
      message: 'Device unregistered successfully'
    });
  } catch (error) {
    console.error('Unregistration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// API to get connected devices (for dashboard)
app.get('/api/v1/devices', (req, res) => {
  try {
    const devices = Array.from(connectedDevices.values())
      .filter(device => device.status === 'active' || device.status === 'connected')
      .map(device => ({
        device_id: device.device_id,
        hostname: device.hostname,
        username: device.username,
        classroom_id: device.classroom_id,
        last_heartbeat: device.last_heartbeat,
        metrics: device.metrics || {},
        status: device.status
      }));
    
    res.json({ devices, count: devices.length });
  } catch (error) {
    console.error('Devices API error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Cleanup inactive devices every 5 minutes
setInterval(() => {
  const now = new Date();
  const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);
  
  for (const [deviceId, device] of connectedDevices.entries()) {
    const lastHeartbeat = new Date(device.last_heartbeat);
    if (lastHeartbeat < fiveMinutesAgo && device.status === 'active') {
      device.status = 'inactive';
      console.log(`Device marked as inactive: ${device.hostname}`);
    }
  }
}, 5 * 60 * 1000);

app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
  console.log('API endpoints available:');
  console.log('  POST /api/v1/register');
  console.log('  POST /api/v1/heartbeat');
  console.log('  POST /api/v1/unregister');
  console.log('  GET  /api/v1/devices');
});
