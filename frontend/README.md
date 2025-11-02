# ScheiniCam Frontend

Modernes Vue.js 3 Frontend für das ScheiniCam Aufnahmesystem.

## Technologie-Stack

- **Framework**: Vue 3 (Composition API)
- **UI Library**: Vuetify 3 (Material Design)
- **State Management**: Pinia
- **Routing**: Vue Router 4
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Sprache**: Deutsch (de-DE)

## Projektstruktur

```
frontend/
├── src/
│   ├── assets/          # Statische Assets (CSS, Bilder)
│   ├── components/      # Wiederverwendbare Komponenten
│   │   ├── DownloadWizard.vue
│   │   ├── TimeSelector.vue
│   │   └── PreviewImage.vue
│   ├── stores/          # Pinia State Management
│   │   ├── recording.js
│   │   ├── admin.js
│   │   └── videos.js
│   ├── views/           # Seiten-Komponenten
│   │   ├── RecordingView.vue
│   │   ├── DownloadView.vue
│   │   ├── AdminView.vue
│   │   └── CheckView.vue
│   ├── services/        # API Services
│   │   └── api.js
│   ├── router/          # Vue Router Konfiguration
│   │   └── index.js
│   ├── plugins/         # Vue Plugins
│   │   └── vuetify.js
│   ├── App.vue          # Haupt-App-Komponente
│   └── main.js          # App Einstiegspunkt
├── public/              # Öffentliche Dateien
├── Dockerfile           # Docker-Konfiguration
├── nginx.conf           # Nginx-Konfiguration
├── package.json         # NPM Abhängigkeiten
└── vite.config.js       # Vite Konfiguration
```

## Features

### 1. Aufnahme-Seite (/)
- Live-Kamerapreview (aktualisiert jede Sekunde)
- Aufnahmestatus-Anzeige
- Aktuelle Uhrzeit
- Anleitung für Benutzer
- Tab-Navigation zwischen Aufnahme und Videoarchiv

### 2. Videoarchiv (/download)
- 4-Schritte-Wizard für Video-Download:
  1. Aufnahme auswählen
  2. Startzeit festlegen (mit Slider und Buttons)
  3. Endzeit festlegen
  4. Export und Download
- Frame-Preview an ausgewählter Zeit
- Zeitanpassung: ±1 Min, ±10 Sek
- Dateigrößenanzeige
- Export-Fortschrittsanzeige

### 3. Admin-Seite (/admin)
- OBS-Verbindungsstatus
- Mute/Unmute-Steuerung
- Manuelle Aufnahme starten/stoppen
- Kamera neu laden
- Logo anzeigen/ausblenden
- Video-Verwaltung (Liste, Löschen)
- Log-Verwaltung
- System herunterfahren

### 4. Check-Seite (/check)
- Audio-Level-Test (2 Sekunden Messung)
- Kamera-Preview
- Kamera neu laden
- Seite neu laden

## Installation & Entwicklung

### Voraussetzungen
- Node.js 18+ und npm
- Backend muss laufen (Port 8000)

### Entwicklungsserver starten

```bash
# Abhängigkeiten installieren
npm install

# Entwicklungsserver starten (http://localhost:3000)
npm run dev
```

### Production Build

```bash
# Production Build erstellen
npm run build

# Build-Vorschau
npm run preview
```

## Docker-Deployment

### Docker Build

```bash
# Docker Image bauen
docker build -t scheinicam-frontend .

# Container starten
docker run -p 80:80 scheinicam-frontend
```

### Mit Docker Compose

Das Frontend ist bereits in die `docker-compose.yml` integriert:

```bash
# Alle Services starten
docker-compose up -d

# Frontend neu bauen
docker-compose up -d --build frontend
```

## API-Integration

Das Frontend kommuniziert mit dem Backend über folgende Endpoints:

### Recording API (`/api/`)
- `GET /api/status` - Aufnahmestatus
- `POST /api/start` - Aufnahme starten
- `POST /api/stop` - Aufnahme stoppen
- `GET /api/current` - Aktuelle Aufnahme
- `GET /api/preview` - Screenshot von OBS

### Admin API (`/admin/`)
- `GET /admin/status` - Admin-Status
- `POST /admin/mute` - Mute/Unmute
- `POST /admin/camera/reload` - Kamera neu laden
- `POST /admin/logo` - Logo-Sichtbarkeit
- `POST /admin/shutdown` - System herunterfahren
- `GET /admin/audio/check` - Audio-Check
- `GET /admin/logs` - Log-Dateien auflisten
- `DELETE /admin/logs` - Alle Logs löschen

### Videos API (`/api/videos/`)
- `GET /api/videos` - Alle Videos
- `GET /api/videos/:id` - Video-Details
- `GET /api/videos/:id/frame` - Frame-Preview
- `POST /api/videos/:id/export` - Subclip exportieren
- `DELETE /api/videos/:id` - Video löschen

## State Management (Pinia)

### Recording Store
Verwaltet Aufnahmestatus, Preview-Bilder und Recording-Aktionen.

### Admin Store
Verwaltet Admin-Funktionen, OBS-Status und Log-Dateien.

### Videos Store
Verwaltet Video-Liste, Export-Prozess und Downloads.

## Komponenten

### DownloadWizard
4-Schritte-Wizard für Video-Download mit Stepper-UI.

### TimeSelector
Interaktiver Zeit-Slider mit:
- Slider für präzise Auswahl
- Quick-Buttons (±1 Min, ±10 Sek)
- Frame-Preview
- Zeit-Anzeige

### PreviewImage
Live-Kamera-Preview mit automatischer Aktualisierung.

## Styling

- **Design System**: Material Design (Vuetify)
- **Responsive**: Mobile-first Design
- **Container Max-Width**: 50em (800px)
- **Theme**: Light Theme mit anpassbaren Farben
- **Icons**: Material Design Icons (@mdi/font)

## Browser-Unterstützung

- Chrome/Edge (neueste Versionen)
- Firefox (neueste Versionen)
- Safari (neueste Versionen)

## Entwicklungshinweise

### Code-Style
- Vue 3 Composition API (`<script setup>`)
- Pinia für State Management (statt Vuex)
- Async/Await für asynchrone Operationen
- Deutsche Sprache für alle UI-Texte

### Performance
- Lazy Loading für Views
- Automatische Komponenten-Imports (Vuetify)
- Vite für schnelles HMR
- Nginx mit Gzip-Kompression

### Best Practices
- Komponentenbasierte Architektur
- Separation of Concerns (Views, Stores, Services)
- Error Handling in API-Calls
- Loading-States für bessere UX

## Lizenz

Copyright © 2025 ScheiniCam
