# ScheinCam V2 - Dockerized

Neuaufbau des ScheinCam-Projekts mit moderner Architektur:
- **Backend**: FastAPI (Python)
- **Frontend**: Noch zu implementieren (z.B. React, Vue, oder Svelte)
- **Deployment**: Docker & Docker Compose

## Projektstruktur

```
scheinicam-v2/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── api/         # API-Routen
│   │   ├── core/        # Konfiguration
│   │   ├── models/      # Datenmodelle
│   │   └── services/    # Business-Logik
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # Frontend (noch zu implementieren)
├── docker-compose.yml   # Orchestrierung
└── README.md
```

## Features

### Backend (FastAPI)

✅ **Implementiert (Grundstruktur)**:
- Modernes FastAPI-Setup mit async/await
- RESTful API-Endpunkte für alle Funktionen
- OBS Studio Integration (WebSocket)
- Automatische Aufnahmeplanung
- Video-Verwaltung und -Export
- Admin-Funktionen
- Konfigurationsmanagement
- Docker-Support

⏳ **Noch zu implementieren**:
- Methoden-Implementierungen in Services
- WebSocket für Live-Updates
- Authentifizierung/Autorisierung (falls gewünscht)
- Unit Tests
- Error-Handling-Verbesserungen

### Frontend

🔜 **Zu planen**:
- Framework-Auswahl (React, Vue, Svelte)
- UI/UX Design
- Video-Player Integration
- Live-Preview
- Admin-Panel
- Responsive Design

## Schnellstart

### Voraussetzungen

- Docker & Docker Compose
- OBS Studio mit WebSocket-Plugin
- Python 3.11+ (für lokale Entwicklung)

### Installation

1. **Repository klonen**
   ```bash
   git clone <repository-url>
   cd scheinicam-v2
   ```

2. **Umgebungsvariablen konfigurieren**
   ```bash
   cd backend
   cp .env.example .env
   # .env bearbeiten und OBS-Passwort eintragen
   ```

3. **Mit Docker Compose starten**
   ```bash
   docker-compose up -d
   ```

4. **API-Dokumentation öffnen**
   ```
   http://localhost:8000/docs
   ```

## Entwicklung

### Backend lokal ausführen

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload
```

### Docker neu bauen

```bash
docker-compose build
docker-compose up -d
```

## API-Übersicht

### Recordings
- `GET /api/recordings/status` - Aufnahmestatus
- `POST /api/recordings/start` - Aufnahme starten
- `POST /api/recordings/stop` - Aufnahme stoppen
- `GET /api/recordings/preview` - Live-Preview

### Videos
- `GET /api/videos/` - Alle Videos
- `POST /api/videos/export` - Video exportieren
- `GET /api/videos/{filename}/download` - Download

### Admin
- `POST /api/admin/mute` - Aufnahme mute/unmute
- `POST /api/admin/camera/reload` - Kamera neu laden
- `GET /api/admin/audio/check` - Audio-Check

### Settings
- `GET /api/settings/` - Einstellungen abrufen
- `PUT /api/settings/` - Einstellungen ändern

Vollständige Dokumentation: `http://localhost:8000/docs`

## Konfiguration

Alle Einstellungen werden über die `.env`-Datei konfiguriert:

### Aufnahmezeiten

```env
START_TIME=19:50:00
END_TIME=22:10:00
SHUTDOWN_TIME=01:00:00
WEEKDAYS=0,1,2,3,4,5,6
```

### OBS-Verbindung

```env
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_password
```

### Weitere Einstellungen

```env
DEBUG=False
TIMEZONE=Europe/Berlin
DELETE_AGE_SECONDS=1209600
CLEANUP_INTERVAL_SECONDS=3600
SHOW_LOGO=True
```

## Migration vom alten System

Das Backend behält die Funktionalität des Original-Projekts:

- ✅ Automatische Aufnahmeplanung
- ✅ OBS Studio Integration
- ✅ Video-Export mit Zeitauswahl
- ✅ Preview-Bilder
- ✅ Admin-Funktionen
- ✅ Automatisches Löschen alter Videos
- ✅ Settings-Management

**Unterschiede:**
- REST API statt Server-Side Rendering
- Asynchrone Verarbeitung
- Docker-basiertes Deployment
- Frontend/Backend-Trennung

## Nächste Schritte

1. **Backend vervollständigen**
   - Service-Methoden implementieren
   - Error-Handling verbessern
   - Tests schreiben

2. **Frontend entwickeln**
   - Framework wählen
   - UI-Komponenten erstellen
   - API-Integration

3. **Deployment**
   - Reverse Proxy (nginx)
   - SSL/TLS Zertifikate
   - Monitoring & Logging

4. **Features**
   - User-Management
   - Multi-Camera Support
   - Cloud-Upload
   - Benachrichtigungen

## Beitragen

Feedback und Contributions sind willkommen!

## Lizenz

Siehe LICENSE.md
