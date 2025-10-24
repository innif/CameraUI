# 🚀 Quick Start Guide

## 1. Vorbereitung

```bash
cd backend

# Umgebungsvariablen konfigurieren
cp .env.example .env
nano .env  # OBS_PASSWORD anpassen!
```

## 2. Lokale Entwicklung (ohne Docker)

```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Verzeichnisse erstellen
mkdir -p videos logs assets

# Optional: Services testen
python dev.py test

# Server starten
python dev.py serve
# oder direkt:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API-Dokumentation:** http://localhost:8000/docs

## 3. Mit Docker

```bash
# Aus dem Hauptverzeichnis
docker-compose up -d

# Logs anschauen
docker-compose logs -f backend

# Stoppen
docker-compose down
```

## 4. Erste API-Calls testen

```bash
# Health Check
curl http://localhost:8000/api/health

# Recording Status
curl http://localhost:8000/api/recordings/status

# Videos auflisten
curl http://localhost:8000/api/videos/

# Preview-Bild holen
curl http://localhost:8000/api/recordings/preview

# Settings anzeigen
curl http://localhost:8000/api/settings/
```

## 5. Troubleshooting

### OBS verbindet nicht
- Ist OBS gestartet?
- WebSocket-Plugin aktiviert?
- Port 4455 offen?
- Passwort in .env korrekt?

### Videos werden nicht gefunden
- Verzeichnis `videos/` existiert?
- JSON-Metadaten vorhanden?

### Import-Fehler
```bash
pip install -r requirements.txt --upgrade
```

### Docker-Probleme
```bash
# Neu bauen
docker-compose build --no-cache
docker-compose up -d
```

## 6. Produktiv-Deployment

1. **Nginx Reverse Proxy** einrichten
2. **SSL/TLS** Zertifikate (Let's Encrypt)
3. **Firewall** konfigurieren
4. **Monitoring** einrichten (z.B. Prometheus)
5. **Backups** für Videos einrichten

## API-Endpoints Übersicht

### Recordings
- `GET /api/recordings/status` - Status
- `POST /api/recordings/start` - Start
- `POST /api/recordings/stop` - Stop
- `GET /api/recordings/preview` - Preview

### Videos
- `GET /api/videos/` - Liste
- `POST /api/videos/export` - Export
- `GET /api/videos/{filename}/download` - Download
- `POST /api/videos/frame` - Frame extrahieren

### Admin
- `POST /api/admin/mute` - Mute/Unmute
- `POST /api/admin/camera/reload` - Kamera reload
- `GET /api/admin/audio/check` - Audio check
- `GET /api/admin/logs` - Logs

### Settings
- `GET /api/settings/` - Abrufen
- `PUT /api/settings/` - Ändern
- `POST /api/settings/save` - Speichern

**Vollständige Docs:** http://localhost:8000/docs
