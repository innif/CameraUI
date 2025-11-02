# 📡 API-Beispiele

Beispiele für alle API-Endpunkte mit curl und Python requests.

## Basis-URL

```
http://localhost:8000
```

---

## 🎥 Recordings API

### Status abrufen
```bash
curl http://localhost:8000/api/recordings/status
```

**Response:**
```json
{
  "connected": true,
  "recording": false,
  "muted": false,
  "current_file": null,
  "current_start_time": null
}
```

### Aufnahme starten
```bash
curl -X POST http://localhost:8000/api/recordings/start
```

**Response:**
```json
{
  "success": true,
  "message": "Recording started",
  "filename": "25-01-24_20-15-30"
}
```

### Aufnahme stoppen
```bash
curl -X POST http://localhost:8000/api/recordings/stop
```

### Preview-Bild abrufen
```bash
curl http://localhost:8000/api/recordings/preview
```

**Response:**
```json
{
  "connected": true,
  "muted": false,
  "image": "data:image/jpg;base64,/9j/4AAQSkZJRg..."
}
```

---

## 📹 Videos API

### Alle Videos auflisten
```bash
curl http://localhost:8000/api/videos/
```

**Response:**
```json
{
  "videos": [
    {
      "filename": "25-01-24_20-15-30",
      "start_time": "2025-01-24T20:15:30",
      "end_time": "2025-01-24T22:30:15"
    }
  ],
  "total": 1
}
```

### Video-Info abrufen
```bash
curl http://localhost:8000/api/videos/25-01-24_20-15-30
```

### Video exportieren (Subclip)
```bash
curl -X POST http://localhost:8000/api/videos/export \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "25-01-24_20-15-30",
    "start_time": "20:30:00",
    "end_time": "21:00:00"
  }'
```

**Response:**
```json
{
  "success": true,
  "filepath": "videos/subclip_25-01-24_20-15-30-900-3000.mp4",
  "download_url": "/videos/subclip_25-01-24_20-15-30-900-3000.mp4"
}
```

### Frame extrahieren
```bash
curl -X POST http://localhost:8000/api/videos/frame \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "25-01-24_20-15-30",
    "timestamp": "20:45:00"
  }'
```

**Response:**
```json
{
  "success": true,
  "image": "data:image/jpg;base64,/9j/4AAQSkZJRg...",
  "timestamp": "20:45:00"
}
```

### Video herunterladen
```bash
curl -O http://localhost:8000/api/videos/25-01-24_20-15-30/download
```

### Neuestes Video
```bash
curl http://localhost:8000/api/videos/newest/info
```

### Video löschen
```bash
curl -X DELETE http://localhost:8000/api/videos/25-01-24_20-15-30
```

---

## 🔧 Admin API

### Admin-Status
```bash
curl http://localhost:8000/api/admin/status
```

**Response:**
```json
{
  "obs": {
    "connected": true,
    "recording": false,
    "muted": false,
    "current_file": null
  },
  "video_count": 5,
  "newest_video": "25-01-24_20-15-30"
}
```

### Video muten
```bash
curl -X POST http://localhost:8000/api/admin/mute \
  -H "Content-Type: application/json" \
  -d '{"muted": true}'
```

### Video unmuten
```bash
curl -X POST http://localhost:8000/api/admin/mute \
  -H "Content-Type: application/json" \
  -d '{"muted": false}'
```

### Kamera neu laden
```bash
curl -X POST http://localhost:8000/api/admin/camera/reload
```

### Logo ein-/ausblenden
```bash
# Logo ausblenden
curl -X POST http://localhost:8000/api/admin/logo \
  -H "Content-Type: application/json" \
  -d '{"visible": false}'

# Logo einblenden
curl -X POST http://localhost:8000/api/admin/logo \
  -H "Content-Type: application/json" \
  -d '{"visible": true}'
```

### Audio-Check
```bash
curl http://localhost:8000/api/admin/audio/check
```

**Response:**
```json
{
  "audio_range": 0.45,
  "working": true,
  "message": "Audio funktioniert"
}
```

### Logs auflisten
```bash
curl http://localhost:8000/api/admin/logs
```

**Response:**
```json
{
  "logs": [
    "log25-01-24--20-15-30.log",
    "log25-01-23--19-50-00.log"
  ],
  "count": 2
}
```

### Log-Datei abrufen
```bash
curl http://localhost:8000/api/admin/logs/log25-01-24--20-15-30.log
```

### Alle Logs löschen
```bash
curl -X DELETE http://localhost:8000/api/admin/logs
```

### System herunterfahren
```bash
# VORSICHT!
curl -X POST http://localhost:8000/api/admin/shutdown
```

---

## ⚙️ Settings API

### Einstellungen abrufen
```bash
curl http://localhost:8000/api/settings/
```

**Response:**
```json
{
  "start_time": "19:50:00",
  "end_time": "22:10:00",
  "shutdown_time": "01:00:00",
  "weekdays": [2, 3, 4, 5, 6],
  "delete_age_days": 14.0,
  "show_logo": true,
  "obs_host": "localhost",
  "obs_port": 4455
}
```

### Einstellungen aktualisieren
```bash
curl -X PUT http://localhost:8000/api/settings/ \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "20:00:00",
    "end_time": "22:00:00",
    "weekdays": [0, 1, 2, 3, 4, 5, 6],
    "show_logo": false
  }'
```

### Einstellungen neu laden
```bash
curl -X POST http://localhost:8000/api/settings/reload
```

### Einstellungen speichern
```bash
curl -X POST http://localhost:8000/api/settings/save
```

---

## 🏥 Health API

### Health-Check
```bash
curl http://localhost:8000/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-24T20:15:30.123456",
  "obs_connected": true,
  "recording": false,
  "version": "2.0.0"
}
```

### Ping
```bash
curl http://localhost:8000/api/ping
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-01-24T20:15:30.123456"
}
```

---

## 🐍 Python Beispiele

### Mit `requests` Bibliothek

```python
import requests

BASE_URL = "http://localhost:8000"

# Status abrufen
response = requests.get(f"{BASE_URL}/api/recordings/status")
print(response.json())

# Aufnahme starten
response = requests.post(f"{BASE_URL}/api/recordings/start")
print(response.json())

# Videos auflisten
response = requests.get(f"{BASE_URL}/api/videos/")
videos = response.json()
print(f"Gefundene Videos: {videos['total']}")

# Video exportieren
export_data = {
    "filename": "25-01-24_20-15-30",
    "start_time": "20:30:00",
    "end_time": "21:00:00"
}
response = requests.post(
    f"{BASE_URL}/api/videos/export",
    json=export_data
)
result = response.json()
if result['success']:
    print(f"Export erfolgreich: {result['download_url']}")

# Frame abrufen
frame_data = {
    "filename": "25-01-24_20-15-30",
    "timestamp": "20:45:00"
}
response = requests.post(
    f"{BASE_URL}/api/videos/frame",
    json=frame_data
)
frame = response.json()
if frame['success']:
    # Base64 Image in frame['image']
    print("Frame erfolgreich abgerufen")

# Settings aktualisieren
settings_update = {
    "start_time": "20:00:00",
    "show_logo": False
}
response = requests.put(
    f"{BASE_URL}/api/settings/",
    json=settings_update
)
print(response.json())
```

### Asynchron mit `httpx`

```python
import httpx
import asyncio

async def main():
    BASE_URL = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Status
        response = await client.get(f"{BASE_URL}/api/recordings/status")
        print(response.json())
        
        # Mehrere Requests parallel
        tasks = [
            client.get(f"{BASE_URL}/api/videos/"),
            client.get(f"{BASE_URL}/api/settings/"),
            client.get(f"{BASE_URL}/api/health")
        ]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(result.json())

asyncio.run(main())
```

---

## 🌐 JavaScript/TypeScript Beispiele

### Mit `fetch` API

```javascript
const BASE_URL = 'http://localhost:8000';

// Status abrufen
async function getStatus() {
  const response = await fetch(`${BASE_URL}/api/recordings/status`);
  const data = await response.json();
  console.log(data);
}

// Aufnahme starten
async function startRecording() {
  const response = await fetch(`${BASE_URL}/api/recordings/start`, {
    method: 'POST'
  });
  const data = await response.json();
  console.log(data);
}

// Video exportieren
async function exportVideo(filename, startTime, endTime) {
  const response = await fetch(`${BASE_URL}/api/videos/export`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      filename: filename,
      start_time: startTime,
      end_time: endTime
    })
  });
  const data = await response.json();
  return data;
}

// Videos auflisten
async function listVideos() {
  const response = await fetch(`${BASE_URL}/api/videos/`);
  const data = await response.json();
  return data.videos;
}

// Settings aktualisieren
async function updateSettings(settings) {
  const response = await fetch(`${BASE_URL}/api/settings/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(settings)
  });
  return await response.json();
}
```

### Mit `axios`

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Status
const status = await api.get('/api/recordings/status');
console.log(status.data);

// Start
const start = await api.post('/api/recordings/start');
console.log(start.data);

// Export
const exportResult = await api.post('/api/videos/export', {
  filename: '25-01-24_20-15-30',
  start_time: '20:30:00',
  end_time: '21:00:00'
});
console.log(exportResult.data);
```

---

## 🧪 Testing mit Postman

1. **Collection importieren:**
   - Neue Collection erstellen: "ScheinCam API"
   - Base URL Variable: `{{base_url}}` = `http://localhost:8000`

2. **Requests hinzufügen:**
   - Alle Endpunkte als Requests
   - Mit Example Responses

3. **Tests schreiben:**
   ```javascript
   pm.test("Status Code is 200", function () {
       pm.response.to.have.status(200);
   });
   
   pm.test("Response has success", function () {
       var jsonData = pm.response.json();
       pm.expect(jsonData.success).to.be.true;
   });
   ```

---

## 📊 Monitoring

### Kontinuierliches Preview-Update (Shell)

```bash
#!/bin/bash
while true; do
  curl -s http://localhost:8000/api/recordings/preview | \
    jq -r '.image' | \
    base64 -d > preview.jpg
  sleep 1
done
```

### Status-Monitoring (Python)

```python
import time
import requests

while True:
    try:
        status = requests.get('http://localhost:8000/api/health').json()
        print(f"Status: {status['status']} | Recording: {status['recording']}")
    except:
        print("Backend nicht erreichbar!")
    time.sleep(5)
```
