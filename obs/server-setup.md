# Server Setup Guide - CameraUI mit OBS Studio

Diese Anleitung beschreibt die vollständige Einrichtung eines Ubuntu-Servers für CameraUI mit OBS Studio im Headless-Modus.

## Inhaltsverzeichnis

1. [Docker Installation](#docker-installation)
2. [CameraUI Setup](#cameraui-setup)
3. [Benutzer-Einrichtung](#benutzer-einrichtung)
4. [Desktop-Umgebung & Remote Desktop](#desktop-umgebung--remote-desktop)
5. [OBS Studio Installation](#obs-studio-installation)
6. [OBS Systemd Service](#obs-systemd-service)
7. [Remote Desktop Konfiguration](#remote-desktop-konfiguration)
8. [Firewall & Netzwerk](#firewall--netzwerk)
9. [System-Optimierungen](#system-optimierungen)
10. [System-Steuerung (Shutdown & Restart)](#system-steuerung-shutdown--restart)
11. [Intel VAAPI Hardware-Beschleunigung](#intel-vaapi-hardware-beschleunigung)

---

## Docker Installation

Zuerst aktualisieren wir das System und installieren Docker:

```bash
sudo apt update
```

### Docker GPG-Schlüssel hinzufügen

```bash
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

### Docker Repository hinzufügen

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

### Docker installieren

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

---

## CameraUI Setup

### Repository klonen und konfigurieren

```bash
git clone https://github.com/innif/CameraUI.git
cd CameraUI
cp .env.example .env
```

### Umgebungsvariablen anpassen

```bash
nano .env
```

Passen Sie die `.env`-Datei nach Ihren Bedürfnissen an.

### Docker Container starten

```bash
sudo docker compose up -d --build
```

---

## Benutzer-Einrichtung

### OBS-Benutzer erstellen

```bash
sudo adduser obsuser
```

**Passwort:** `obsuser`

### Benutzer zu sudo-Gruppe hinzufügen

```bash
sudo usermod -aG sudo obsuser
```

### Benutzer zu erforderlichen Gruppen hinzufügen

```bash
sudo usermod -aG video,audio,plugdev obsuser
```

### Linger aktivieren (für systemd User Services)

```bash
sudo loginctl enable-linger obsuser
```

---

## Desktop-Umgebung & Remote Desktop

### Erforderliche Pakete installieren

```bash
sudo apt install -y libpam-modules libpam-modules-bin pulseaudio xfce4 xfce4-goodies xrdp xvfb dbus-x11
```

---

## OBS Studio Installation

### OBS PPA hinzufügen und installieren

```bash
sudo add-apt-repository -y ppa:obsproject/obs-studio
sudo apt update
sudo apt install -y obs-studio ffmpeg
```

---

## OBS Systemd Service

### Service-Datei erstellen

```bash
sudo nano /etc/systemd/system/obs.service
```

### Service-Konfiguration

Fügen Sie folgenden Inhalt ein:

```ini
[Unit]
Description=OBS Studio (headless)
Wants=network-online.target
After=network-online.target systemd-logind.service

[Service]
Type=simple
User=obsuser
# Session-ähnliche Umgebung für Gerätezugriff:
Environment=XDG_RUNTIME_DIR=/run/user/1001
Environment=DISPLAY=:99
Environment=QT_X11_NO_MITSHM=1

# Laufzeitverzeichnis sicherstellen
ExecStartPre=/bin/mkdir -p /run/user/1001
ExecStartPre=/bin/chown obsuser:obsuser /run/user/1001

# Pulseaudio nur starten, wenn vorhanden (sonst überspringen)
ExecStartPre=/bin/bash -lc 'command -v pulseaudio >/dev/null 2>&1 && pulseaudio --start --log-target=journal || true'

# Virtuelles Display + OBS
ExecStart=/usr/bin/xvfb-run --auto-servernum --server-args='-screen 0 1920x1080x24' /usr/bin/obs --minimize-to-tray

Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Service aktivieren und starten

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now obs.service
sudo systemctl restart obs.service
```

### System neu starten

```bash
sudo reboot now
```

---

## Remote Desktop Konfiguration

### XFCE Session konfigurieren

```bash
sudo bash -c 'echo xfce4-session > /home/obsuser/.xsession'
sudo chown obsuser:obsuser /home/obsuser/.xsession
```

### XRDP Startwm.sh anpassen

```bash
sudo sed -i 's/^test -x \/etc\/x11\/Xsession/#&/' /etc/xrdp/startwm.sh
sudo sed -i 's/^exec \/etc\/x11\/Xsession/#&/' /etc/xrdp/startwm.sh
echo "xfce4-session" | sudo tee -a /etc/xrdp/startwm.sh
```

### XRDP Service neu starten

```bash
sudo systemctl restart xrdp
```

---

## Firewall & Netzwerk

### OBS WebSocket Port freigeben

```bash
sudo ufw allow 4455/tcp
```

---

## System-Optimierungen

### Shared Directory erstellen

```bash
sudo mkdir -p /srv/share
sudo chmod 2775 /srv/share
sudo chown root:users /srv/share
```

### Sleep/Suspend deaktivieren

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

---

## System-Steuerung (Shutdown & Restart)

Die CameraUI-Web-Oberfläche bietet Buttons zum Herunterfahren und Neustarten des Servers. Da die Anwendung in Docker läuft, sind spezielle Berechtigungen erforderlich.

### Sudo-Berechtigungen einrichten

Erstellen Sie eine sudoers-Datei für Docker-Container:

```bash
sudo visudo -f /etc/sudoers.d/docker-shutdown
```

Fügen Sie folgende Zeilen ein:

```
root ALL=(ALL) NOPASSWD: /sbin/shutdown
root ALL=(ALL) NOPASSWD: /sbin/reboot
```

Speichern und schließen Sie die Datei (Ctrl+X, dann Y, dann Enter).

### Docker-Container neu starten

Nach der Einrichtung der sudoers-Datei müssen die Container neu gebaut werden:

```bash
cd ~/CameraUI
sudo docker compose down
sudo docker compose up -d --build
```

### Funktionsweise testen

1. Öffnen Sie die CameraUI-Web-Oberfläche
2. Navigieren Sie zur Admin-Seite oder Check-Seite
3. Klicken Sie auf "Neustart" oder "Herunterfahren"
4. Bestätigen Sie die Aktion im Dialog

Der Server sollte sich nun entsprechend neu starten oder herunterfahren.

### Fehlerbehebung

Wenn die Funktionen nicht funktionieren, prüfen Sie die Logs:

```bash
sudo docker compose logs backend --tail 50
```

Stellen Sie sicher, dass:
- Die sudoers-Datei korrekt erstellt wurde: `sudo cat /etc/sudoers.d/docker-shutdown`
- Der Container im privileged-Modus läuft (in `docker-compose.yml` konfiguriert)
- Die sudoers-Datei im Container gemountet ist

---

## Intel VAAPI Hardware-Beschleunigung

Für Intel Haswell-GPUs (HD 4400/4600) auf Ubuntu 24.04.

### Basis-Pakete installieren

```bash
sudo apt update
sudo apt install intel-media-va-driver-non-free vainfo
```

### VAAPI-Setup-Script erstellen

Erstellen Sie ein Script `enable-vaapi-haswell-ubuntu24_v3.sh`:

```bash
#!/usr/bin/env bash
# enable-vaapi-haswell-ubuntu24_v3.sh
# Reaktiviert VAAPI H.264 auf Ubuntu 24.04 für Intel Haswell (HD 4400/4600)
# Holt libva* + i965* gezielt aus Jammy (22.04), pinned & mit --allow-downgrades.

set -euo pipefail

need_root() { [[ $(id -u) -eq 0 ]] || { echo "Bitte mit sudo/root ausführen."; exit 1; }; }
need_root

echo "==> System:"
. /etc/os-release
echo "Ubuntu: $PRETTY_NAME"
echo "Kernel: $(uname -r)"
echo

# --- 0) Aufräumen / Konflikte beseitigen ---
echo "==> Entferne inkompatible/konfliktende Pakete (falls vorhanden)…"
apt-get -y remove intel-media-va-driver intel-media-va-driver-non-free i965-va-driver i965-va-driver-shaders || true

# --- 1) Jammy-Sources & Pinning nur für benötigte Pakete ---
echo "==> Richte Jammy (22.04) Quellen & Pinning ein…"
cat >/etc/apt/sources.list.d/jammy-i965.list <<'EOF'
deb http://archive.ubuntu.com/ubuntu jammy main universe
deb http://archive.ubuntu.com/ubuntu jammy-updates main universe
deb http://security.ubuntu.com/ubuntu jammy-security main universe
EOF

cat >/etc/apt/preferences.d/pin-i965.pref <<'EOF'
Package: i965-va-driver i965-va-driver-shaders libva2 libva-drm2 libva-x11-2 libva-wayland2 vainfo
Pin: release n=jammy
Pin-Priority: 1001

Package: *
Pin: release n=jammy
Pin-Priority: -10
EOF

apt-get update

# Helfer alias: Installieren aus Jammy mit Downgrades erlaubt
install_jammy() {
  DEBIAN_FRONTEND=noninteractive apt-get -y -t jammy --allow-downgrades install "$@"
}

# --- 2) Zuerst libva-Stack passend (verhindert ABI-Konflikte) ---
echo "==> Installiere libva-Stack aus Jammy (mit Downgrades)…"
install_jammy libva2 libva-drm2 libva-x11-2 libva-wayland2 vainfo

# --- 3) Dann i965-Treiberpaar (Reihenfolge + Downgrades) ---
echo "==> Installiere i965-Treiber aus Jammy (mit Downgrades)…"
# Shader-Paket zuerst weg (falls apt es erneut ziehen will)
apt-get -y remove i965-va-driver-shaders || true
# Haupttreiber zuerst:
install_jammy i965-va-driver
# Dann das dazu passende Shaders-Paket:
install_jammy i965-va-driver-shaders

# --- 4) Sanity-Check: Treiberdatei vorhanden? ---
DRV="/usr/lib/x86_64-linux-gnu/dri/i965_drv_video.so"
if [[ ! -f "$DRV" ]]; then
  echo "FEHLER: $DRV existiert nicht. Prüfe apt-Policy/Pinning."
  apt-cache policy i965-va-driver i965-va-driver-shaders libva2 | sed -n '1,120p'
  exit 2
fi

# --- 5) Env & Gruppenrechte setzen ---
echo "==> Setze ENV & Gruppenrechte…"
grep -q '^LIBVA_DRIVER_NAME=i965$' /etc/environment || echo 'LIBVA_DRIVER_NAME=i965' >> /etc/environment
export LIBVA_DRIVER_NAME=i965
export LIBVA_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri

# den aufrufenden User + obsuser in video/render aufnehmen
for u in "$SUDO_USER" obsuser; do
  id "$u" &>/dev/null || continue
  usermod -aG video "$u" || true
  usermod -aG render "$u" || true
done

# --- 6) Geräte & kurze Tests ---
echo "==> /dev/dri:"
ls -l /dev/dri || true
echo

echo "==> vainfo (Kurz, DRM wenn möglich)…"
set +e
vainfo --display drm --device /dev/dri/renderD128 2>/dev/null | sed -n '1,120p'
VRC=$?
if [[ $VRC -ne 0 ]]; then
  vainfo | sed -n '1,120p'
fi
set -e

if command -v ffmpeg >/dev/null 2>&1; then
  echo "==> ffmpeg Test (5s, h264_vaapi)…"
  ffmpeg -v error -f lavfi -i testsrc2=size=1280x720:rate=30 \
        -vaapi_device /dev/dri/renderD128 \
        -vf 'format=nv12,hwupload' \
        -t 5 -c:v h264_vaapi /tmp/vaapi-test.mp4 && echo "OK: /tmp/vaapi-test.mp4"
else
  echo "Hinweis: ffmpeg nicht installiert – Test übersprungen."
fi

echo
echo "==> Fertig. Einmal ab-/anmelden oder rebooten, damit Gruppen & /etc/environment greifen."
echo "==> In OBS: Output -> Advanced -> Encoder: H.264 (VAAPI), Device: /dev/dri/renderD128, Pixel Format: NV12."
```

### Script ausführbar machen und starten

```bash
chmod +x enable-vaapi-haswell-ubuntu24_v3.sh
sudo ./enable-vaapi-haswell-ubuntu24_v3.sh
```

### System neu starten

```bash
sudo reboot now
```

### OBS VAAPI-Einstellungen

Nach dem Neustart in OBS konfigurieren:
- **Output** → **Advanced** → **Encoder:** H.264 (VAAPI)
- **Device:** `/dev/dri/renderD128`
- **Pixel Format:** NV12

---

## Logs & Debugging

### OBS Service Status prüfen

```bash
sudo systemctl status obs.service
```

### OBS Logs in Echtzeit anzeigen

```bash
journalctl -u obs.service -f
```

---

## Hinweise

- Der `obsuser` hat das Passwort `obsuser` - ändern Sie dies in einer Produktionsumgebung!
- Stellen Sie sicher, dass alle erforderlichen Ports in Ihrer Firewall geöffnet sind
- Bei Problemen mit der Hardware-Beschleunigung prüfen Sie mit `vainfo`, ob der Treiber korrekt geladen wurde
- Die UID 1001 im systemd-Service muss ggf. angepasst werden, wenn der obsuser eine andere UID hat (prüfen mit `id obsuser`)
