# Frontend Projektstruktur

## Verzeichnisbaum

```
frontend/
│
├── public/                     # Statische Dateien (direkt kopiert)
│
├── src/
│   │
│   ├── assets/                 # CSS, Bilder, Fonts
│   │   └── main.css           # Globale Styles
│   │
│   ├── components/             # Wiederverwendbare Komponenten
│   │   ├── DownloadWizard.vue # 4-Schritte-Download-Wizard
│   │   ├── TimeSelector.vue   # Zeit-Slider mit Preview & Buttons
│   │   └── PreviewImage.vue   # Live-Kamera-Preview
│   │
│   ├── views/                  # Seiten-Komponenten (Routes)
│   │   ├── RecordingView.vue  # Hauptseite (/ - Aufnahme + Archiv-Tabs)
│   │   ├── DownloadView.vue   # Download-Seite (/download)
│   │   ├── AdminView.vue      # Admin-Panel (/admin)
│   │   └── CheckView.vue      # System-Check (/check)
│   │
│   ├── stores/                 # Pinia State Management
│   │   ├── recording.js       # Aufnahme-Status & Steuerung
│   │   ├── admin.js           # Admin-Funktionen & OBS-Status
│   │   └── videos.js          # Video-Liste & Export
│   │
│   ├── services/               # API & Services
│   │   └── api.js             # Axios HTTP Client mit allen Endpoints
│   │
│   ├── router/                 # Vue Router
│   │   └── index.js           # Route-Definitionen
│   │
│   ├── plugins/                # Vue Plugins
│   │   └── vuetify.js         # Vuetify Konfiguration (Material Design)
│   │
│   ├── App.vue                 # Haupt-App-Komponente (Layout)
│   └── main.js                 # App-Einstiegspunkt
│
├── Dockerfile                  # Multi-Stage Docker Build
├── nginx.conf                  # Nginx Reverse Proxy Config
├── vite.config.js              # Vite Build-Tool Config
├── package.json                # NPM Dependencies
├── index.html                  # HTML Entry Point
├── .gitignore                  # Git Ignore
├── README.md                   # Projekt-Dokumentation
└── STRUCTURE.md               # Diese Datei
```

## Komponenten-Hierarchie

```
App.vue
├── RecordingView.vue (/)
│   ├── PreviewImage.vue
│   └── DownloadWizard.vue
│       └── TimeSelector.vue
│
├── DownloadView.vue (/download)
│   └── DownloadWizard.vue
│       └── TimeSelector.vue
│
├── AdminView.vue (/admin)
│   └── PreviewImage.vue
│
└── CheckView.vue (/check)
    └── PreviewImage.vue
```

## Datenfluss

```
┌─────────────┐
│   Views     │  (UI-Komponenten)
└──────┬──────┘
       │ ruft auf
       ↓
┌─────────────┐
│   Stores    │  (Pinia State Management)
└──────┬──────┘
       │ ruft auf
       ↓
┌─────────────┐
│  Services   │  (API-Calls)
└──────┬──────┘
       │ HTTP
       ↓
┌─────────────┐
│   Backend   │  (FastAPI)
└─────────────┘
```

## State Management (Pinia Stores)

### recording.js
**Verantwortlich für**: Aufnahme-Status, Live-Preview, Recording-Steuerung

**State**:
- `isRecording` - Ob aktuell aufgenommen wird
- `isConnected` - OBS-Verbindungsstatus
- `currentFile` - Aktuell laufende Aufnahme
- `previewImage` - Base64 Screenshot von OBS
- `loading` - Loading-State für UI
- `error` - Fehlermeldungen

**Actions**:
- `fetchStatus()` - Aufnahmestatus abrufen
- `startRecording()` - Aufnahme starten
- `stopRecording()` - Aufnahme stoppen
- `fetchCurrentFile()` - Aktuelle Datei-Info
- `fetchPreview()` - Screenshot abrufen

### admin.js
**Verantwortlich für**: Admin-Funktionen, System-Steuerung

**State**:
- `isMuted` - Mute-Status
- `obsStatus` - OBS-Verbindungsstatus & Details
- `filesInfo` - Datei-Statistiken
- `audioCheckResult` - Audio-Test-Ergebnis
- `logs` - Log-Dateien-Liste
- `loading` - Loading-State
- `error` - Fehlermeldungen

**Actions**:
- `fetchStatus()` - Admin-Status abrufen
- `setMute(muted)` - Aufnahme muten/unmuten
- `reloadCamera()` - Kamera neu laden
- `setLogoVisibility(visible)` - Logo ein-/ausblenden
- `shutdownSystem()` - System herunterfahren
- `checkAudio()` - Audio-Level testen
- `fetchLogs()` - Log-Dateien abrufen
- `deleteLogs()` - Alle Logs löschen

### videos.js
**Verantwortlich für**: Video-Verwaltung, Export, Download

**State**:
- `videos` - Liste aller Videos
- `selectedVideo` - Ausgewähltes Video
- `previewFrame` - Frame-Preview (Base64)
- `exportedFile` - Exportierte Datei-Info
- `loading` - Loading-State
- `exporting` - Export-Fortschritt
- `error` - Fehlermeldungen

**Actions**:
- `fetchVideos()` - Alle Videos abrufen
- `selectVideo(id)` - Video auswählen
- `fetchFrame(id, timestamp)` - Frame-Preview abrufen
- `exportSubclip(id, start, end)` - Video-Subclip exportieren
- `downloadVideo(filename)` - Video herunterladen
- `deleteVideo(id)` - Video löschen
- `clearExportedFile()` - Export-Status zurücksetzen

## API-Endpoints (services/api.js)

### Recording API
```javascript
recording: {
  getStatus()        // GET /api/status
  start()            // POST /api/start
  stop()             // POST /api/stop
  getCurrent()       // GET /api/current
  getPreview()       // GET /api/preview
}
```

### Admin API
```javascript
admin: {
  getStatus()                    // GET /admin/status
  setMute(muted)                 // POST /admin/mute
  reloadCamera()                 // POST /admin/camera/reload
  setLogo(visible)               // POST /admin/logo
  shutdown()                     // POST /admin/shutdown
  checkAudio()                   // GET /admin/audio/check
  getLogs()                      // GET /admin/logs
  getLogFile(filename)           // GET /admin/logs/{filename}
  deleteLogs()                   // DELETE /admin/logs
}
```

### Videos API
```javascript
videos: {
  getAll()                       // GET /api/videos
  getById(id)                    // GET /api/videos/{id}
  getFrame(id, timestamp)        // GET /api/videos/{id}/frame
  exportSubclip(id, start, end)  // POST /api/videos/{id}/export
  download(filename)             // GET /videos/{filename}
  delete(id)                     // DELETE /api/videos/{id}
}
```

## Router-Konfiguration

```javascript
routes: [
  { path: '/', name: 'recording', component: RecordingView },
  { path: '/download', name: 'download', component: DownloadView },
  { path: '/admin', name: 'admin', component: AdminView },
  { path: '/check', name: 'check', component: CheckView }
]
```

## Build-Prozess (Docker Multi-Stage)

### Stage 1: Build
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
```

### Stage 2: Production
```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Nginx Reverse Proxy

```
Browser → Nginx (Port 80)
            ├─→ /api/*     → Backend (Port 8000)
            ├─→ /admin/*   → Backend (Port 8000)
            ├─→ /videos/*  → Backend (Port 8000)
            └─→ /*         → Vue.js SPA (index.html)
```

## Entwicklungs-Workflow

1. **Lokale Entwicklung**:
   ```bash
   npm run dev  # Vite Dev Server auf Port 3000
   ```

2. **Production Build**:
   ```bash
   npm run build  # Erstellt dist/ Ordner
   ```

3. **Docker Build**:
   ```bash
   docker build -t scheinicam-frontend .
   ```

4. **Docker Compose**:
   ```bash
   docker-compose up -d
   ```

## Key Features pro Komponente

### RecordingView
✅ Tab-Navigation (Aufnahme / Videoarchiv)
✅ Live-Preview (1s Update)
✅ Aufnahmestatus-Badge
✅ Aktuelle Uhrzeit
✅ OBS-Verbindungsstatus
✅ Anleitung (expandable)

### DownloadWizard
✅ 4-Schritte-Wizard (Stepper)
✅ Video-Auswahl (Dropdown)
✅ Start-/Endzeit-Selektion
✅ Export-Fortschritt
✅ Download-Button mit Dateigröße

### TimeSelector
✅ Zeit-Slider (0 bis Video-Dauer)
✅ Quick-Buttons (-1min, -10s, +10s, +1min)
✅ Frame-Preview
✅ Formatierte Zeit-Anzeige

### PreviewImage
✅ Auto-Refresh (1s Intervall)
✅ Live-Badge
✅ Loading-State
✅ Responsive Bild

### AdminView
✅ Mute/Unmute (große Buttons)
✅ Manuelle Recording-Steuerung
✅ OBS-Status
✅ Kamera-Reload
✅ Logo-Steuerung
✅ Video-Liste mit Delete
✅ Log-Verwaltung
✅ Shutdown mit Bestätigung

### CheckView
✅ Audio-Test (2s Messung)
✅ Audio-Ergebnis-Anzeige
✅ Kamera-Preview
✅ Kamera-Reload
✅ Seite neu laden

## Dependencies

### Production
- `vue`: ^3.4.21
- `vue-router`: ^4.3.0
- `pinia`: ^2.1.7
- `vuetify`: ^3.5.10
- `@mdi/font`: ^7.4.47
- `axios`: ^1.6.7

### Development
- `vite`: ^5.1.5
- `@vitejs/plugin-vue`: ^5.0.4
- `vite-plugin-vuetify`: ^2.0.1
