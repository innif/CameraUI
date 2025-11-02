#!/usr/bin/env bash
# setup_obs_headless.sh
# Ubuntu Server: Xfce + xrdp + OBS (ppa) + headless systemd Autostart + Template-Config + Docker + CameraUI
set -euo pipefail

# ----------------------------- Konfig -----------------------------
OBS_USER="${OBS_USER:-obsuser}"
OBS_PASS="${OBS_PASS:-}"
OBS_XRES="${OBS_XRES:-1920}"
OBS_YRES="${OBS_YRES:-1080}"

# Default-Startflags inkl. deiner Wünsche:
# --multi = mehrere Instanzen erlaubt
# --disable-shutdown-check = keine Crash-Abfrage
# --minimize-to-tray = nicht im Weg
OBS_ARGS_DEFAULT="${OBS_ARGS:---multi --disable-shutdown-check --minimize-to-tray}"

TEMPLATE_DIR="/opt/obs-config-template"
ENV_FILE="/etc/obs-headless/env"
SERVICE_FILE="/etc/systemd/system/obs.service"
WRAPPER="/usr/local/bin/obs-headless-start.sh"
SAVE_TEMPLATE="/usr/local/bin/obs-save-template.sh"

# CameraUI Repository
CAMERA_UI_REPO="https://github.com/innif/CameraUI.git"
CAMERA_UI_DIR="/opt/CameraUI"

# Zufallspasswort, falls keins gesetzt
rand_pw () { tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16; echo; }
if [[ -z "${OBS_PASS}" ]]; then
  OBS_PASS="$(rand_pw)"
fi

echo "=========================================================="
echo "   CameraUI + OBS Headless Setup für Ubuntu Server"
echo "=========================================================="
echo "==> Benutzer: ${OBS_USER}"
echo "==> Display (Xvfb): ${OBS_XRES}x${OBS_YRES}"
echo "==> OBS Start-Args: ${OBS_ARGS_DEFAULT}"
echo "==> CameraUI wird installiert nach: ${CAMERA_UI_DIR}"
echo

# ----------------------------- Pakete -----------------------------
export DEBIAN_FRONTEND=noninteractive
sudo apt update
sudo apt install -y \
  xfce4 xfce4-goodies \
  xrdp xorgxrdp dbus-x11 \
  software-properties-common rsync xvfb \
  ffmpeg libgl1 libxkbcommon-x11-0 libxcb-xinerama0 \
  pulseaudio v4l-utils \
  libpam-modules libpam-modules-bin \
  git curl ca-certificates gnupg lsb-release

# OBS PPA
sudo add-apt-repository -y ppa:obsproject/obs-studio
sudo apt update
sudo apt install -y obs-studio

# xrdp-Rechte
sudo adduser xrdp ssl-cert || true

# ----------------------------- Docker installieren -----------------------------
echo "==> Installiere Docker..."

# Alte Docker-Versionen entfernen
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Docker Repository einrichten
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker installieren
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker-Dienst starten
sudo systemctl enable --now docker

# Benutzer zur docker-Gruppe hinzufügen
sudo usermod -aG docker "${OBS_USER}" || true
if [[ -n "${SUDO_USER:-}" ]]; then
  sudo usermod -aG docker "${SUDO_USER}" || true
fi

echo "==> Docker installiert: $(docker --version)"
echo "==> Docker Compose installiert: $(docker compose version)"

# ----------------------------- Benutzer -----------------------------
if ! id -u "${OBS_USER}" >/dev/null 2>&1; then
  echo "==> Lege Benutzer ${OBS_USER} an"
  sudo adduser --disabled-password --gecos "" "${OBS_USER}"
fi
echo "${OBS_USER}:${OBS_PASS}" | sudo chpasswd
sudo usermod -aG sudo,video,audio,plugdev "${OBS_USER}" || true

# Xfce als Standard-Session für RDP
echo xfce4-session | sudo tee "/home/${OBS_USER}/.xsession" >/dev/null
sudo chown "${OBS_USER}:${OBS_USER}" "/home/${OBS_USER}/.xsession"

# „Linger“ erlauben (hilft bei user-scoped Diensten/Runtime)
sudo loginctl enable-linger "${OBS_USER}" || true

# ----------------------------- RDP aktivieren -----------------------------
sudo systemctl enable --now xrdp

# Firewall (optional)
if command -v ufw >/dev/null 2>&1; then
  if sudo ufw status | grep -q "Status: active"; then
    sudo ufw allow 3389/tcp || true   # RDP
    sudo ufw allow 4455/tcp || true   # OBS-WebSocket (falls in OBS aktiv)
  fi
fi

# ----------------------------- Polkit für Docker Shutdown/Reboot -----------------------------
echo "==> Konfiguriere Polkit-Regeln für Docker Shutdown/Reboot..."

# Stelle sicher, dass Polkit installiert ist
sudo apt install -y polkitd || sudo apt install -y policykit-1 || true

# Erstelle Polkit-Regel für Docker-Container
POLKIT_RULES="/etc/polkit-1/rules.d/10-docker-shutdown.rules"
sudo mkdir -p /etc/polkit-1/rules.d

sudo bash -c "cat > '${POLKIT_RULES}'" <<'POLKIT_EOF'
// Erlaube Docker-Container Shutdown und Reboot über D-Bus
polkit.addRule(function(action, subject) {
    if ((action.id == "org.freedesktop.login1.power-off" ||
         action.id == "org.freedesktop.login1.power-off-multiple-sessions" ||
         action.id == "org.freedesktop.login1.reboot" ||
         action.id == "org.freedesktop.login1.reboot-multiple-sessions") &&
        subject.isInGroup("docker")) {
        return polkit.Result.YES;
    }
});
POLKIT_EOF

echo "==> Polkit-Regel erstellt: ${POLKIT_RULES}"

# Stelle sicher, dass D-Bus läuft
sudo systemctl enable --now dbus || true
sudo systemctl restart polkit || sudo systemctl restart polkitd || true

echo "==> D-Bus und Polkit konfiguriert"

# ----------------------------- Template-Ordner -----------------------------
sudo mkdir -p "${TEMPLATE_DIR}"
sudo chown -R "${OBS_USER}:${OBS_USER}" "${TEMPLATE_DIR}"

# ----------------------------- Env-Datei -----------------------------
sudo mkdir -p "$(dirname "${ENV_FILE}")"
sudo bash -c "cat > '${ENV_FILE}'" <<EOF
# /etc/obs-headless/env
OBS_XRES=${OBS_XRES}
OBS_YRES=${OBS_YRES}
OBS_ARGS="${OBS_ARGS_DEFAULT}"
EOF

# ----------------------------- Wrapper (Startlogik) -----------------------------
sudo bash -c "cat > '${WRAPPER}'" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${OBS_XRES:=1920}"
: "${OBS_YRES:=1080}"
: "${OBS_ARGS:=--multi --disable-shutdown-check --minimize-to-tray}"

USER_NAME="${USER_NAME:-$(whoami)}"
USER_UID="$(id -u "${USER_NAME}")"
CFG_HOME="/home/${USER_NAME}/.config"
TEMPLATE_DIR="/opt/obs-config-template"

# Runtime-Verzeichnis für Audio/IPC bereitstellen
export XDG_RUNTIME_DIR="/run/user/${USER_UID}"
mkdir -p "${XDG_RUNTIME_DIR}" || true
chown "${USER_NAME}:${USER_NAME}" "${XDG_RUNTIME_DIR}" || true

# Saubere (goldene) Config einspielen – verhindert blockierende Dialoge
mkdir -p "${CFG_HOME}"
rm -rf "${CFG_HOME}/obs-studio" || true
rsync -a "${TEMPLATE_DIR}/" "${CFG_HOME}/obs-studio/" || true
chown -R "${USER_NAME}:${USER_NAME}" "${CFG_HOME}/obs-studio" || true

# Pulseaudio (falls vorhanden) starten, aber nicht hart verlangen
if command -v pulseaudio >/dev/null 2>&1; then
  pulseaudio --start --log-target=journal || true
fi

# Headless via Xvfb starten
exec /usr/bin/xvfb-run --auto-servernum \
  --server-args="-screen 0 ${OBS_XRES}x${OBS_YRES}x24" \
  /usr/bin/obs ${OBS_ARGS}
EOF
sudo chmod +x "${WRAPPER}"

# ----------------------------- Template speichern (Helper) -----------------------------
sudo bash -c "cat > '${SAVE_TEMPLATE}'" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
USER_NAME="${OBS_USER:-obsuser}"
SRC="/home/${USER_NAME}/.config/obs-studio/"
DST="/opt/obs-config-template/"
if [[ ! -d "${SRC}" ]]; then
  echo "OBS-Config unter ${SRC} nicht gefunden. Starte OBS einmal per RDP, konfiguriere und beende es sauber."
  exit 1
fi
sudo rsync -a --delete "${SRC}" "${DST}"
sudo chown -R "${USER_NAME}:${USER_NAME}" "${DST}"
echo "Template aktualisiert: ${DST}"
EOF
sudo chmod +x "${SAVE_TEMPLATE}"

# ----------------------------- systemd Service -----------------------------
# UID des Users ermitteln für XDG_RUNTIME_DIR
OBS_UID="$(id -u "${OBS_USER}")"

sudo bash -c "cat > '${SERVICE_FILE}'" <<EOF
[Unit]
Description=OBS Studio (headless autostart)
Wants=network-online.target
After=network-online.target systemd-logind.service

[Service]
Type=simple
User=${OBS_USER}

# Session-ähnliche Umgebung (ohne PAMName-Fehler)
Environment=XDG_RUNTIME_DIR=/run/user/${OBS_UID}
Environment=DISPLAY=:99
Environment=QT_X11_NO_MITSHM=1
EnvironmentFile=${ENV_FILE}

# Laufzeitverzeichnis sicherstellen
ExecStartPre=/bin/mkdir -p /run/user/${OBS_UID}
ExecStartPre=/bin/chown ${OBS_USER}:${OBS_USER} /run/user/${OBS_UID}

# Pulseaudio nur starten, wenn vorhanden (nicht fatal)
ExecStartPre=/bin/bash -lc 'command -v pulseaudio >/dev/null 2>&1 && pulseaudio --start --log-target=journal || true'

# Start-Wrapper erledigt: frische Config + XDG_RUNTIME_DIR + Xvfb + OBS
Environment=USER_NAME=${OBS_USER}
ExecStart=${WRAPPER}

Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now obs.service

# ----------------------------- CameraUI Repository klonen -----------------------------
echo
echo "==> Klone CameraUI Repository..."

if [[ -d "${CAMERA_UI_DIR}" ]]; then
  echo "==> Verzeichnis ${CAMERA_UI_DIR} existiert bereits. Überspringe Klonen."
else
  sudo git clone "${CAMERA_UI_REPO}" "${CAMERA_UI_DIR}"
  sudo chown -R "${OBS_USER}:${OBS_USER}" "${CAMERA_UI_DIR}"
  echo "==> Repository geklont nach ${CAMERA_UI_DIR}"
fi

# ----------------------------- .env Konfiguration -----------------------------
echo
echo "==> Konfiguriere CameraUI (.env Datei)..."

ENV_PATH="${CAMERA_UI_DIR}/.env"

# Funktion zum Lesen von Benutzereingaben mit Standardwert
read_input() {
  local prompt="$1"
  local default="$2"
  local value

  if [[ -n "$default" ]]; then
    read -p "${prompt} [${default}]: " value
    echo "${value:-$default}"
  else
    read -p "${prompt}: " value
    echo "${value}"
  fi
}

# Funktion zum Lesen von Passwörtern (ohne Anzeige)
read_password() {
  local prompt="$1"
  local default="$2"
  local value

  if [[ -n "$default" ]]; then
    read -sp "${prompt} [zufällig generiert]: " value
    echo >&2  # Neue Zeile nach Passwort-Eingabe
    echo "${value:-$default}"
  else
    read -sp "${prompt}: " value
    echo >&2  # Neue Zeile nach Passwort-Eingabe
    echo "${value}"
  fi
}

echo
echo "Bitte gib die Konfigurationswerte für CameraUI ein:"
echo "(Drücke Enter für Standardwerte)"
echo

# OBS WebSocket Konfiguration
OBS_WS_PASSWORD=$(read_password "OBS WebSocket Passwort" "$(rand_pw)")
echo

# Aufnahmezeiten
START_TIME=$(read_input "Aufnahmestart (HH:MM:SS)" "19:50:00")
END_TIME=$(read_input "Aufnahmeende (HH:MM:SS)" "22:10:00")
SHUTDOWN_TIME=$(read_input "System-Shutdown-Zeit (HH:MM:SS)" "01:00:00")

# Wochentage
echo
echo "Wochentage für Aufnahmen (0=Montag, 6=Sonntag):"
WEEKDAYS=$(read_input "Wochentage (Komma-getrennt)" "2,3,4,5,6")

# Web-UI Passwort
echo
WEB_PASSWORD=$(read_password "Web-UI Passwort" "$(rand_pw)")
echo

# .env Datei erstellen
sudo bash -c "cat > '${ENV_PATH}'" <<EOF
# Application Settings
DEBUG=False
APP_NAME=ScheinCam

# OBS Connection
OBS_HOST=host.docker.internal
OBS_PORT=4455
OBS_PASSWORD=${OBS_WS_PASSWORD}

# Recording Schedule (24-hour format)
START_TIME=${START_TIME}
END_TIME=${END_TIME}
SHUTDOWN_TIME=${SHUTDOWN_TIME}

# Weekdays (0=Monday, 6=Sunday)
WEEKDAYS="${WEEKDAYS}"

# File Management
CLEANUP_INTERVAL_SECONDS=3600
DELETE_AGE_SECONDS=1209600
VIDEO_DIRECTORY=videos
ASSETS_DIRECTORY=assets
LOGS_DIRECTORY=logs

# UI Settings
SHOW_LOGO=True

# WebSocket
WS_HEARTBEAT_INTERVAL=30

# Authentication
WEB_PASSWORD=${WEB_PASSWORD}
EOF

sudo chown "${OBS_USER}:${OBS_USER}" "${ENV_PATH}"
echo "==> .env Datei erstellt: ${ENV_PATH}"

# ----------------------------- Docker Compose starten -----------------------------
echo
echo "==> Baue und starte Docker Container..."

cd "${CAMERA_UI_DIR}"
sudo -u "${OBS_USER}" docker compose up -d --build

echo "==> Docker Container gestartet"
echo "==> Warte 5 Sekunden auf Container-Start..."
sleep 5

# Status prüfen
sudo -u "${OBS_USER}" docker compose ps

# ----------------------------- Ausgabe -----------------------------
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo
echo "=========================================================="
echo "                    INSTALLATION ABGESCHLOSSEN"
echo "=========================================================="
echo
echo "SYSTEM-INFORMATIONEN:"
echo "  Server IP:           ${IP:-<SERVER-IP>}"
echo "  Benutzer:            ${OBS_USER}"
echo "  Passwort:            ${OBS_PASS}"
echo
echo "OBS STUDIO (Headless):"
echo "  Status:              $(systemctl is-active obs.service)"
echo "  Logs ansehen:        journalctl -u obs.service -f"
echo "  Neustart:            sudo systemctl restart obs.service"
echo
echo "  WICHTIG - OBS WebSocket einrichten:"
echo "    1) RDP-Verbindung:       ${IP:-<SERVER-IP>}:3389"
echo "    2) OBS öffnen und konfigurieren:"
echo "       - Werkzeuge → WebSocket-Server-Einstellungen"
echo "       - Server aktivieren"
echo "       - Port: 4455"
echo "       - Passwort: ${OBS_WS_PASSWORD}"
echo "    3) Szenen/Quellen einrichten"
echo "    4) OBS sauber beenden"
echo "    5) Template speichern:   sudo ${SAVE_TEMPLATE}"
echo "    6) Dienst neustarten:    sudo systemctl restart obs.service"
echo
echo "CAMERAUI WEB-INTERFACE:"
echo "  URL:                 http://${IP:-<SERVER-IP>}"
echo "  Web-UI Passwort:     ${WEB_PASSWORD}"
echo "  Konfiguration:       ${CAMERA_UI_DIR}/.env"
echo "  Logs:                ${CAMERA_UI_DIR}/backend/logs/"
echo
echo "  Aufnahmezeiten:"
echo "    Start:             ${START_TIME}"
echo "    Ende:              ${END_TIME}"
echo "    Shutdown:          ${SHUTDOWN_TIME}"
echo "    Wochentage:        ${WEEKDAYS}"
echo
echo "DOCKER:"
echo "  Status:              docker compose ps"
echo "  Logs ansehen:        cd ${CAMERA_UI_DIR} && docker compose logs -f"
echo "  Neustart:            cd ${CAMERA_UI_DIR} && docker compose restart"
echo "  Stoppen:             cd ${CAMERA_UI_DIR} && docker compose down"
echo "  Neu bauen:           cd ${CAMERA_UI_DIR} && docker compose up -d --build"
echo
echo "NÄCHSTE SCHRITTE:"
echo "  1. Per RDP verbinden und OBS WebSocket konfigurieren (siehe oben)"
echo "  2. CameraUI Web-Interface aufrufen: http://${IP:-<SERVER-IP>}"
echo "  3. Bei Problemen Logs prüfen:"
echo "     - OBS:       journalctl -u obs.service -f"
echo "     - CameraUI:  cd ${CAMERA_UI_DIR} && docker compose logs -f"
echo
echo "=========================================================="
