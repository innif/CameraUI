# 🏗️ Architektur-Übersicht

## System-Komponenten

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    (zu implementieren)                      │
│                  React / Vue / Svelte                       │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  API Routes                            │ │
│  │  • /api/recordings  • /api/videos                      │ │
│  │  • /api/admin       • /api/settings                    │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                         │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │                  Services                              │ │
│  │  ┌──────────────┐   ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ OBS Service  │   │ File Service │  │  Scheduler   │ │ │
│  │  └──────┬───────┘   └──────┬───────┘  └──────┬───────┘ │ │
│  │         │                  │                 │         │ │
│  │         │                  │                 │         │ │
│  └─────────┼──────────────────┼─────────────────┼─────────┘ │
└────────────┼──────────────────┼─────────────────┼───────────┘
             │                  │                 │
             │                  │                 │
     ┌───────▼──────┐    ┌──────▼───────┐   ┌─────▼──────┐
     │              │    │              │   │            │
     │ OBS Studio   │    │  File System │   │   Timer    │
     │ (WebSocket)  │    │  (videos/)   │   │   (Cron)   │
     │              │    │              │   │            │
     └──────────────┘    └──────────────┘   └────────────┘
```

## Datenfluss

### 1. Automatische Aufnahme

```
Timer (19:50 Uhr)
    ↓
RecordingScheduler._check_recording_schedule()
    ↓
RecordingScheduler.start_recording()
    ↓
OBSService.start_recording()
    ↓
OBS Studio startet Aufnahme
    ↓
VideoFile wird erstellt
    ↓
FileService.add_file()
    ↓
Metadata → videos/XX-XX-XX_XX-XX-XX.json
```

### 2. Video-Export (Subclip)

```
User Request: POST /api/videos/export
    {filename, start_time, end_time}
    ↓
videos.export_video()
    ↓
FileService.export_subclip()
    ↓
ffmpeg_extract_subclip() [moviepy]
    ↓
subclip_XX.mp4 erstellt
    ↓
Download-URL zurückgeben
```

### 3. Preview-Bild

```
Frontend Poll: GET /api/recordings/preview
    ↓
recordings.get_preview_image()
    ↓
OBSService.get_screenshot()
    ↓
OBS WebSocket: GetSourceScreenshot
    ↓
Base64 JPEG zurück
    ↓
Frontend zeigt Bild an
```

## Datei-Struktur

```
backend/
├── app/
│   ├── api/                    # HTTP Endpoints
│   │   ├── recordings.py       # Aufnahme-Steuerung
│   │   ├── videos.py           # Video-Verwaltung
│   │   ├── admin.py            # Admin-Funktionen
│   │   ├── settings.py         # Konfiguration
│   │   └── health.py           # Health-Checks
│   ├── core/
│   │   └── config.py           # Settings (Pydantic)
│   ├── models/
│   │   └── video.py            # VideoFile, Requests, Responses
│   └── services/               # Business Logic
│       ├── obs_service.py      # OBS WebSocket Client
│       ├── file_service.py     # Video-Dateien verwalten
│       └── recording_scheduler.py  # Automatische Planung
├── main.py                     # FastAPI App
├── dev.py                      # Dev/Test-Tools
└── requirements.txt
```

## Service-Verantwortlichkeiten

### OBSService
- **Verbindung** zu OBS Studio (WebSocket)
- **Aufnahme** starten/stoppen
- **Screenshots** erstellen
- **Audio-Check**
- **Kamera** neu laden
- **Szenen** wechseln (mute/unmute)

### FileService
- **Dateien** scannen und verwalten
- **Subclips** exportieren (ffmpeg)
- **Frames** extrahieren (cv2)
- **Metadaten** speichern (JSON)
- **Alte Videos** löschen

### RecordingScheduler
- **Zeitplan** überwachen
- **Automatisch** aufnehmen (Start/End-Zeit)
- **Wochentage** beachten
- **System-Shutdown** planen

## API-Design-Prinzipien

### RESTful
- `GET` - Daten abrufen
- `POST` - Neue Ressourcen / Aktionen
- `PUT` - Ressourcen aktualisieren
- `DELETE` - Ressourcen löschen

### Response-Format
```json
{
  "success": true,
  "data": {...},
  "message": "Optional message"
}
```

### Error-Format
```json
{
  "detail": "Error message"
}
```

## Asynchrone Verarbeitung

- **FastAPI** → async/await
- **OBS WebSocket** → Threading (obsws_python)
- **File Operations** → `asyncio.to_thread()`
- **Video Export** → Background (moviepy)

## Skalierung & Performance

### Aktuell
- Single-Process FastAPI
- Lokaler Dateisystem-Storage
- In-Memory Video-Liste

### Zukünftig möglich
- **Gunicorn** mit mehreren Workern
- **Redis** für State-Management
- **S3/MinIO** für Video-Storage
- **PostgreSQL** für Metadaten
- **Celery** für Background-Jobs
- **WebSocket** für Live-Updates

## Sicherheit

### Aktuell
- Basis HTTP (für lokales Netzwerk)

### Empfohlen für Produktion
- **HTTPS** (TLS/SSL)
- **Authentication** (JWT)
- **Rate Limiting**
- **Input Validation** (bereits via Pydantic)
- **CORS** Configuration
- **API Keys** für Admin-Endpoints

## Monitoring

### Logs
- Strukturierte Logs in `logs/`
- Python `logging` Modul
- Rotation empfohlen

### Metriken (vorgeschlagen)
- Prometheus Exporter
- Grafana Dashboard
- Alert-Manager

### Health Checks
- `/api/health` - System Status
- `/api/ping` - Simple Liveness

## Deployment-Optionen

### 1. Docker Compose (empfohlen für Start)
```yaml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./videos:/app/videos"]
```

### 2. Systemd Service
```ini
[Unit]
Description=ScheinCam Backend

[Service]
ExecStart=/path/to/venv/bin/uvicorn main:app
WorkingDirectory=/path/to/backend
```

### 3. Kubernetes (für größere Deployments)
- Deployment + Service
- PersistentVolumeClaim für Videos
- Ingress für HTTPS

## Erweiterungsmöglichkeiten

1. **Multi-Camera Support**
   - Mehrere OBS-Instanzen
   - Kamera-Auswahl in API

2. **User Management**
   - Authentication
   - Permissions
   - User-spezifische Videos

3. **Cloud Integration**
   - Auto-Upload zu YouTube
   - S3 Backup
   - CDN für Downloads

4. **Notifications**
   - E-Mail bei Aufnahme-Start
   - Slack/Discord Integration
   - Error-Alerts

5. **Advanced Features**
   - Live-Streaming
   - Real-time Transcoding
   - AI-basierte Szenen-Erkennung
   - Automatische Highlights
